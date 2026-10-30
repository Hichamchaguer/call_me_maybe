from pydantic import BaseModel
import json
from typing import Dict


class Prompt(BaseModel):
    prompt: str

class parameters(BaseModel):
    type: str

class returns_type(BaseModel):
    type: str

class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, parameters]
    returns: returns_type