from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    text: str

class Conversation(BaseModel):
    phone_number: str
    messages: List[Message]
