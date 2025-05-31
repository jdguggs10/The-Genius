"""
Step 5 Integration: Response Logger Service
Integrates confidence scoring logging into the response flow.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models import StructuredAdvice
from app.services.confidence_scoring import confidence_scoring_service

logger = logging.getLogger(__name__)

class ResponseLogger:
    """
    Service for logging responses with confidence scoring.
    Integrates Step 5 confidence calibration into the response pipeline.
    """
    
    def __init__(self):
        """Initialize the response logger."""
        self.confidence_service = confidence_scoring_service
        logger.info("Response logger initialized with confidence scoring")
    
    def log_response(
        self,
        advice: StructuredAdvice,
        user_query: str,
        conversation_context: Optional[List[Dict]] = None,
        model_used: str = "unknown",
        web_search_used: bool = False,
        response_id: Optional[str] = None
    ) -> Optional[int]:
        """
        Log a response with confidence scoring.
        Returns the log entry ID if successful, None if failed.
        """
        try:
            # Extract confidence score
            confidence_score = advice.confidence_score
            if confidence_score is None:
                logger.warning("Response has no confidence score, using default 0.5")
                confidence_score = 0.5
            
            # Prepare response text
            response_text = self._format_response_text(advice)
            
            # Log the entry
            entry_id = self.confidence_service.log_confidence_entry(
                response_text=response_text,
                confidence_score=confidence_score,
                user_query=user_query,
                model_used=model_used,
                web_search_used=web_search_used,
                conversation_context=self._serialize_conversation_context(conversation_context),
                response_id=response_id
            )
            
            logger.info(f"Logged response {entry_id} with confidence {confidence_score}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")
            return None
    
    def _format_response_text(self, advice: StructuredAdvice) -> str:
        """Format the advice into a text representation for logging."""
        parts = []
        
        if advice.main_advice:
            parts.append(f"Main Advice: {advice.main_advice}")
        
        if advice.reasoning:
            parts.append(f"Reasoning: {advice.reasoning}")
        
        if advice.alternatives:
            alternatives_text = "; ".join(advice.alternatives)
            parts.append(f"Alternatives: {alternatives_text}")
        
        return " | ".join(parts) if parts else "No advice provided"
    
    def _serialize_conversation_context(self, conversation_context: Optional[List[Dict]]) -> Optional[Dict]:
        """Serialize conversation context for storage."""
        if not conversation_context:
            return None
        
        try:
            # Summarize conversation context to avoid storing too much data
            context_summary = {
                "message_count": len(conversation_context),
                "last_messages": conversation_context[-3:] if len(conversation_context) > 3 else conversation_context,
                "serialized_at": datetime.utcnow().isoformat()
            }
            return context_summary
        except Exception as e:
            logger.error(f"Failed to serialize conversation context: {e}")
            return {"error": "Failed to serialize context"}
    
    def update_response_outcome(self, response_id: str, outcome: bool, feedback_notes: Optional[str] = None) -> bool:
        """
        Update the outcome for a previously logged response.
        This is called when user feedback is received about the advice quality.
        """
        try:
            success = self.confidence_service.update_outcome(response_id, outcome, feedback_notes)
            if success:
                logger.info(f"Updated outcome for response {response_id}: {outcome}")
            else:
                logger.warning(f"Failed to update outcome for response {response_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating response outcome: {e}")
            return False
    
    def get_recent_logs(self, limit: int = 20) -> List[Dict]:
        """Get recent confidence logs for monitoring."""
        try:
            return self.confidence_service.get_recent_entries(limit)
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    def get_confidence_stats(self, days_back: int = 7) -> Dict:
        """Get confidence statistics for monitoring."""
        try:
            brier_stats = self.confidence_service.calculate_brier_score(days_back)
            distribution = self.confidence_service.get_confidence_distribution(days_back)
            
            return {
                "brier_score": brier_stats,
                "distribution": distribution,
                "period_days": days_back,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting confidence stats: {e}")
            return {"error": str(e)}

# Global service instance
response_logger = ResponseLogger() 