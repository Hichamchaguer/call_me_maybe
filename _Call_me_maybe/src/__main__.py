import argparse
from src.load_json import load_ft_definition, load_prompt
from src.constraint_decoding import buildPrompt, load_vocab, get_next_token, valid_token, isValidJson
from llm_sdk.llm_sdk import Small_LLM_Model
import json
import os

def parsing():

    parser = argparse.ArgumentParser(
        prog='CallMeMaybe',
        description='Introduction to function calling in LLMs'
    )


    # arguments 
    parser.add_argument(
        '--input',
        type=str,
        help='Input string to be processed',
        default='data/input/functions_definition.json'
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
    ft_definition = load_ft_definition(src='data/input/functions_definition.json')
    if not ft_definition:
        raise RuntimeError("No function definitions found in the provided JSON file.")
    prompts = load_prompt(src='data/input/function_calling_tests.json')
    if not prompts:
        raise RuntimeError("No prompts found in the provided JSON file.")
    generated_prompt = buildPrompt(ft_definition)
    # call the LLM Qwen/Qwen3-0.6B
    try:
        model = Small_LLM_Model(model_name=args.model)
    except OSError as e:
        raise RuntimeError(f"Failed to load the model '{args.model}'. Ensure the model name is correct and you have access to it.")
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
        for _ in range(50):
            logits = model.get_logits_from_input_ids(generated_list + generated_token)
            next_token = get_next_token(logits, valid)
            generated_token.append(next_token)

            decoded = model.decode(generated_token)
            is_valid_json = isValidJson(decoded)
            if is_valid_json:
                load_json = json.loads(is_valid_json)
                break

        res.append({
            "prompt": prompt,
            "name": load_json.get("name", "none"),
            "args": load_json.get("arguments", {})
        })

        if load_json.get("name", "none") != "none":
            print(f'>>>>>>>> {load_json.get("name")}, {load_json.get("arguments")}')
        else:
            print(f'>>>>>>>> No matching function found for prompt: "{prompt}"')

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")