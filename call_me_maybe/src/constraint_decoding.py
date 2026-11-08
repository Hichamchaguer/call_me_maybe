import json
# from llm_sdk.llm_sdk import Small_LLM_Model as _model


def isValidJson(_str: str):
    find = _str.find('{')
    if find == -1:
        return 0

    count = 0
    in_string = False
    escape = False

    for i in range(find, len(_str)):
        ch = _str[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == '{':
                count += 1
            elif ch == '}':
                count -= 1
                if count == 0:
                    candidate = _str[find:i+1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        return 0
    return 0


def get_next_token(logits, vocab):
    return max(
        vocab,
        key=lambda i: logits[i] if i in vocab else float('-inf')
    )


def valid_token(vocab: dict):
    json_safe = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJ"
        "KLMNOPQRSTUVWXYZ0123456789*_.,:;+-/\\'!?()[]{}\"ĠĊ"
        )
    valid = set()
    for token, token_id in vocab.items():
        if all(char in json_safe for char in token):
            valid.add(token_id)
    return valid


def buildPrompt(functionDifinition):

    prompt = [
        "You are an expert function calling assistant.",
        "Your task is to call a function matching the user's intent.",
        "If NO function matches the user's intent, set name: \"none\".",
        "Never invent parameters. ONLY use the exact parameter names listed in the function definition.",
        "For regex operations, use standard regular expressions (e.g. \\d+ for numbers, \\bword\\b for whole words, [aeiouAEIOU] for vowels).",
        "",
        "Available functions:"
    ]

    for func in functionDifinition:
        params_str = ", ".join(
            f"{name}: {info.type}"
            for name, info in func.parameters.items()
        )
        prompt.append(f"- {func.name}({params_str}): {func.description}")

    prompt.append(
        '\nRespond ONLY with a JSON object: {"name": "<function_name>", "parameters": {<key_value_pairs>}}'
    )
    return "\n".join(prompt)


def load_vocab(_model):

    vocab = _model.get_path_to_tokenizer_file()
    with open(vocab, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
    raw_vocab = vocab_data.get('model', {}).get('vocab', {})
    return raw_vocab
