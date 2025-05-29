from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Message(BaseModel):
    role: str
    content: str

class AdviceRequest(BaseModel):
    conversation: List[Message]
    players: list[str] | None = None
    model: Optional[str] = None  # Optional model specification
    enable_web_search: Optional[bool] = False  # Option to enable web search
    prompt_type: Optional[Literal["default", "detailed", "baseball", "football", "basketball"]] = "default"  # Prompt type selection

# New/Updated Models for Structured JSON Output
class AdviceAlternative(BaseModel):
    player: str = Field(..., description="The name of the alternative player or choice.")
    reason: Optional[str] = Field(None, description="The reason why this is an alternative.")

class StructuredAdvice(BaseModel):
    main_advice: str = Field(..., description="The primary piece of advice, e.g., 'Start Player A over Player B'. Concise and direct.")
    reasoning: Optional[str] = Field(None, description="The detailed reasoning and context behind the main advice.")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="A confidence score for the advice, between 0.0 and 1.0. Higher is more confident.")
    alternatives: Optional[List[AdviceAlternative]] = Field(None, description="A list of alternative considerations or players.")
    model_identifier: Optional[str] = Field(None, description="Identifier of the AI model that generated this advice.")

    class Config:
        # Pydantic model config if needed, e.g., for aliasing or example generation
        # For now, standard config is fine.
        pass

# AdviceResponse is no longer used by the streaming /advice endpoint, 
# but can be kept if there are other non-streaming use cases or for reference.
class AdviceResponse(BaseModel):
    reply: str
    model: Optional[str] = None  # Model used for generating the response