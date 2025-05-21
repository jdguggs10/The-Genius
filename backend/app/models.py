from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class AdviceRequest(BaseModel):
    conversation: List[Message]
    players: list[str] | None = None
    model: Optional[str] = None  # Optional model specification
    enable_web_search: Optional[bool] = False  # Option to enable web search

class AdviceResponse(BaseModel):
    reply: str
    model: Optional[str] = None  # Model used for generating the response