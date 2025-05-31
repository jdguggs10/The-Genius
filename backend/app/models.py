from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class Message(BaseModel):
    role: str
    content: str

class AdviceRequest(BaseModel):
    conversation: List[Message]
    players: list[str] | None = None
    model: Optional[str] = None  # Optional model specification
    enable_web_search: Optional[bool] = None  # None = use automatic discipline, True/False = force
    search_override: Optional[str] = None  # User commands like "/nosrch" to bypass search
    prompt_type: Optional[Literal["default", "detailed", "baseball", "football", "basketball"]] = "default"  # Prompt type selection
    previous_response_id: Optional[str] = None  # For OpenAI conversation state management
    use_step2_architecture: Optional[bool] = True  # Enable Step 2 slim prompt architecture

# New/Updated Models for Structured JSON Output
class AdviceAlternative(BaseModel):
    player: str = Field(..., description="The name of the alternative player or choice.")
    reason: Optional[str] = Field(None, description="The reason why this is an alternative.")

class StructuredAdvice(BaseModel):
    """
    Structured format for AI advice responses that works with both streaming
    and non-streaming contexts while supporting the OpenAI Responses API format.
    """
    main_advice: str = Field(description="Primary recommendation")
    reasoning: Optional[str] = Field(default=None, description="Detailed explanation of the recommendation")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence level from 0.0 to 1.0")
    alternatives: Optional[List[str]] = Field(default=None, description="Alternative considerations or options")
    model_identifier: Optional[str] = Field(default=None, description="Model used for generating the response")

    class Config:
        # Pydantic model config if needed, e.g., for aliasing or example generation
        # For now, standard config is fine.
        pass

# Step 5: Confidence Scoring Models
class ConfidenceLogEntry(BaseModel):
    """Pydantic model for confidence scoring log entries."""
    response_text: str = Field(description="The full response text")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    user_query: str = Field(description="Original user query")
    conversation_context: Optional[str] = Field(default=None, description="JSON serialized conversation context")
    model_used: str = Field(description="Model identifier used for response")
    web_search_used: bool = Field(description="Whether web search was used")
    outcome: Optional[bool] = Field(default=None, description="Ground truth outcome: True if advice was correct, False if incorrect, None if unknown")
    feedback_timestamp: Optional[datetime] = Field(default=None, description="When outcome feedback was received")
    response_id: Optional[str] = Field(default=None, description="OpenAI response ID for tracking")

class OutcomeFeedback(BaseModel):
    """Model for receiving outcome feedback."""
    response_id: str = Field(description="ID of the response to provide feedback for")
    outcome: bool = Field(description="True if advice was correct/helpful, False if incorrect/unhelpful")
    feedback_notes: Optional[str] = Field(default=None, description="Optional feedback notes")

# SQLAlchemy Database Models for Step 5
Base = declarative_base()

class ConfidenceLog(Base):
    """SQLAlchemy model for storing confidence scoring logs."""
    __tablename__ = "confidence_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    response_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    user_query = Column(Text, nullable=False)
    conversation_context = Column(Text, nullable=True)  # JSON string
    model_used = Column(String(100), nullable=False)
    web_search_used = Column(Boolean, nullable=False, default=False)
    outcome = Column(Boolean, nullable=True)  # None until feedback received
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    feedback_timestamp = Column(DateTime, nullable=True)
    response_id = Column(String(200), nullable=True, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'response_text': self.response_text,
            'confidence_score': self.confidence_score,
            'user_query': self.user_query,
            'conversation_context': self.conversation_context,
            'model_used': self.model_used,
            'web_search_used': self.web_search_used,
            'outcome': self.outcome,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'feedback_timestamp': self.feedback_timestamp.isoformat() if self.feedback_timestamp else None,
            'response_id': self.response_id
        }

# AdviceResponse is no longer used by the streaming /advice endpoint, 
# but can be kept if there are other non-streaming use cases or for reference.
class AdviceResponse(BaseModel):
    reply: str
    model: Optional[str] = None  # Model used for generating the response