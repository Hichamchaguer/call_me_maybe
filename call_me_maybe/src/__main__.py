import argparse
from src.load_json import load_ft_definition, load_prompt
from src.constraint_decoding import (
    buildPrompt,
    load_vocab,
    get_next_token,
    valid_token,
    isValidJson
)

from llm_sdk.llm_sdk import Small_LLM_Model
import json
import os


def parsing():

    parser = argparse.ArgumentParser(
        prog='CallMeMaybe',
        description='Introduction to function calling in LLMs'
    )

    parser.add_argument(
        '--functions_definition',
        type=str,
        help='Functions definition JSON file path',
        default='data/input/functions_definition.json'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input string to be processed',
        default='data/input/function_calling_tests.json'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output string to be processed',
        default='data/output/functions_results.json'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Model to be used for processing',
        default='Qwen/Qwen3-0.6B'
    )

    return parser.parse_args()


def main() -> None:
    print("Hello from call-me-maybe!")
    args = parsing()
    print()
    ft_definition = load_ft_definition(
        src=args.functions_definition
    )
    if not ft_definition:
        raise RuntimeError("No function definitions found.")

    # Create parameter schema lookup for type casting
    param_types = {
        func.name: {p_name: p_info.type for p_name, p_info in func.parameters.items()}
        for func in ft_definition
    }
    prompts = load_prompt(args.input)
    if not prompts:
        raise RuntimeError("No prompts found in the provided JSON file.")
    generated_prompt = buildPrompt(ft_definition)
    # call the LLM Qwen/Qwen3-0.6B
    try:
        model = Small_LLM_Model(model_name=args.model)
    except OSError as e:
        raise RuntimeError(f"Failed to load '{args.model}'.{str(e)}.")
    print()
    vocab = load_vocab(model)
    valid = valid_token(vocab)
    is_valid_json = 0
    res = []
    for p in prompts:
        prompt = p.prompt
        full_prompt = f'{generated_prompt}\n\n Me : {prompt}\n assistant:'
        encoded = model.encode(full_prompt)
        generated_list = encoded[0].tolist()

        generated_token = []
        generated_token.extend(model.encode('{"name": "')[0].tolist())
        load_json = {}
        for _ in range(128):
            logits = model.get_logits_from_input_ids(
                generated_list + generated_token
            )
            next_token = get_next_token(logits, valid)
            generated_token.append(next_token)

            decoded = model.decode(generated_token)
            valid_json_str = isValidJson(decoded)
            if valid_json_str:
                try:
                    load_json = json.loads(valid_json_str)
                    break
                except Exception:
                    pass

        fn_name = load_json.get("name", "none")
        raw_params = load_json.get("parameters", load_json.get("arguments", {}))

        # Filter out keys not present in function signature and cast types
        casted_params = {}
        if isinstance(raw_params, dict) and fn_name in param_types:
            allowed_params = param_types[fn_name]
            for p_name, p_val in raw_params.items():
                if p_name not in allowed_params:
                    continue
                expected_type = allowed_params[p_name]
                if expected_type == "number":
                    try:
                        casted_params[p_name] = float(p_val)
                    except (ValueError, TypeError):
                        casted_params[p_name] = p_val
                elif expected_type == "integer":
                    try:
                        casted_params[p_name] = int(p_val)
                    except (ValueError, TypeError):
                        casted_params[p_name] = p_val
                elif expected_type == "string":
                    casted_params[p_name] = str(p_val)
                elif expected_type == "boolean":
                    casted_params[p_name] = bool(p_val)
                else:
                    casted_params[p_name] = p_val
        elif isinstance(raw_params, dict):
            casted_params = raw_params

        res.append({
            "prompt": prompt,
            "name": fn_name,
            "parameters": casted_params
        })

        if fn_name != "none":
            print(f'{fn_name}, {casted_params}')
        else:
            print(f'No matching function found for prompt: "{prompt}"')

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
