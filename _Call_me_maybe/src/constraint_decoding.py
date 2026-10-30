import json
from llm_sdk.llm_sdk import Small_LLM_Model as _model



def isValidJson(_str: str):

    find = _str.find('{')
    if find == -1:
        return 0

    count = 0
    for i in range(find, len(_str)):
        if _str[i] == '{':
            count += 1
        if _str[i] == '}':
            count -= 1
        if count == 0:
            return _str
    return 0

def get_next_token(logits, vocab):
    return max(
        vocab,
        key=lambda i: logits[i] if i in vocab else float('-inf')
    )

def valid_token(vocab: dict):
    json_safe = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_.,:;+-/\\'!?()[]{}\"ĠĊ")
    valid = set()
    for token, token_id in vocab.items():
        if all(char in json_safe for char in token):
            valid.add(token_id)
    return valid

def buildPrompt(functionDifinition):

    prompt = [

            "STRICT SYSTEM RULE: Use ONLY a matching function from the list below.",
            "If NO function matches the user's intent (even if types match), set name: \"none\".",
            "Never use an unrelated function for a different task.",
            "Available functions:"
    ]

    for func in functionDifinition:
        get_next_line = ", ".join(f'{name}, {info.type}' for name, info in func.parameters.items())
        prompt.append(f' -{func.name}({get_next_line}): {func.description}')
    prompt.append('\nOUTPUT ONLY Valid JSON : {"name": <func>, "arguments": {<args>}}')
    return prompt


def load_vocab(_model):

    vocab = _model.get_path_to_tokenizer_file()
    with open(vocab, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
    raw_vocab = vocab_data.get('model', {}).get('vocab', {})
    return raw_vocab
