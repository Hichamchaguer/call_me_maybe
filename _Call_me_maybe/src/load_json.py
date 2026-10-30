import json
from src.ft_definition import FunctionDefinition, Prompt


def load_prompt(src: str):
    try:
        with open(src, 'r') as f:
            prompt_data = json.load(f)
        return [Prompt(**p) for p in prompt_data]
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {src}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON format in file: {src}")


def load_ft_definition(src: str):
    try:
        with open(src, 'r') as f:
            ft_definition = json.load(f)
        return [FunctionDefinition(**func) for func in ft_definition]
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {src}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON format in file: {src}")


