"""
Step 5: Confidence Scoring Service
Implements confidence scoring calibration as per prompt improvement guide.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Base, ConfidenceLog, ConfidenceLogEntry, OutcomeFeedback

logger = logging.getLogger(__name__)

class ConfidenceScoringService:
    """
    Service for managing confidence scoring logs and calibration.
    Implements Step 5 from the prompt improvement guide.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the confidence scoring service."""
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'sqlite:///./confidence_logs.db'
        )
        
        # Create engine and session factory
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        
        logger.info(f"Confidence scoring service initialized with database: {self.database_url}")
    
    def get_db_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def log_confidence_entry(
        self,
        response_text: str,
        confidence_score: float,
        user_query: str,
        model_used: str,
        web_search_used: bool = False,
        conversation_context: Optional[Dict] = None,
        response_id: Optional[str] = None
    ) -> int:
        """
        Log a confidence scoring entry to the database.
        Returns the entry ID.
        """
        db = self.get_db_session()
        try:
            # Serialize conversation context if provided
            context_json = json.dumps(conversation_context) if conversation_context else None
            
            entry = ConfidenceLog(
                response_text=response_text,
                confidence_score=confidence_score,
                user_query=user_query,
                conversation_context=context_json,
                model_used=model_used,
                web_search_used=web_search_used,
                response_id=response_id,
                timestamp=datetime.utcnow()
            )
            
            db.add(entry)
            db.commit()
            db.refresh(entry)
            
            logger.info(f"Logged confidence entry {entry.id} with score {confidence_score}")
            return entry.id
            
        except SQLAlchemyError as e:
            logger.error(f"Error logging confidence entry: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def update_outcome(self, response_id: str, outcome: bool, feedback_notes: Optional[str] = None) -> bool:
        """
        Update the outcome for a logged entry.
        Returns True if successful, False if entry not found.
        """
        db = self.get_db_session()
        try:
            entry = db.query(ConfidenceLog).filter(ConfidenceLog.response_id == response_id).first()
            
            if not entry:
                logger.warning(f"No confidence log entry found for response_id: {response_id}")
                return False
            
            entry.outcome = outcome
            entry.feedback_timestamp = datetime.utcnow()
            
            db.commit()
            logger.info(f"Updated outcome for entry {entry.id}: {outcome}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating outcome: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def calculate_brier_score(self, days_back: int = 7) -> Dict:
        """
        Calculate Brier score for entries with known outcomes from the last N days.
        Returns Brier score and related statistics.
        """
        db = self.get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get entries with known outcomes from the specified period
            entries = db.query(ConfidenceLog).filter(
                ConfidenceLog.outcome.isnot(None),
                ConfidenceLog.timestamp >= cutoff_date
            ).all()
            
            if not entries:
                return {
                    "brier_score": None,
                    "entries_count": 0,
                    "period_days": days_back,
                    "message": "No entries with outcomes found for the specified period"
                }
            
            # Calculate Brier score
            total_score = 0.0
            for entry in entries:
                # Brier score: (predicted_probability - actual_outcome)^2
                actual_outcome = 1.0 if entry.outcome else 0.0
                squared_error = (entry.confidence_score - actual_outcome) ** 2
                total_score += squared_error
            
            brier_score = total_score / len(entries)
            
            # Additional statistics
            correct_predictions = sum(1 for entry in entries if entry.outcome)
            avg_confidence = sum(entry.confidence_score for entry in entries) / len(entries)
            
            result = {
                "brier_score": brier_score,
                "entries_count": len(entries),
                "correct_predictions": correct_predictions,
                "accuracy": correct_predictions / len(entries),
                "avg_confidence": avg_confidence,
                "period_days": days_back,
                "calculation_date": datetime.utcnow().isoformat(),
                "needs_calibration": brier_score > 0.25  # From guide threshold
            }
            
            logger.info(f"Calculated Brier score: {brier_score:.4f} for {len(entries)} entries")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error calculating Brier score: {e}")
            raise
        finally:
            db.close()
    
    def get_confidence_distribution(self, days_back: int = 30) -> Dict:
        """
        Get confidence score distribution and accuracy by confidence bands.
        """
        db = self.get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            entries = db.query(ConfidenceLog).filter(
                ConfidenceLog.outcome.isnot(None),
                ConfidenceLog.timestamp >= cutoff_date
            ).all()
            
            if not entries:
                return {"message": "No entries with outcomes found"}
            
            # Define confidence bands
            bands = [
                (0.0, 0.5, "low"),
                (0.5, 0.7, "medium"),
                (0.7, 0.9, "high"),
                (0.9, 1.0, "very_high")
            ]
            
            distribution = {}
            for min_conf, max_conf, band_name in bands:
                band_entries = [
                    entry for entry in entries 
                    if min_conf <= entry.confidence_score < max_conf
                ]
                
                if band_entries:
                    correct = sum(1 for entry in band_entries if entry.outcome)
                    avg_confidence = sum(entry.confidence_score for entry in band_entries) / len(band_entries)
                    
                    distribution[band_name] = {
                        "count": len(band_entries),
                        "accuracy": correct / len(band_entries),
                        "avg_confidence": avg_confidence,
                        "range": f"{min_conf}-{max_conf}"
                    }
                else:
                    distribution[band_name] = {
                        "count": 0,
                        "accuracy": None,
                        "avg_confidence": None,
                        "range": f"{min_conf}-{max_conf}"
                    }
            
            return {
                "distribution": distribution,
                "total_entries": len(entries),
                "period_days": days_back
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting confidence distribution: {e}")
            raise
        finally:
            db.close()
    
    def get_recent_entries(self, limit: int = 50, include_pending: bool = True) -> List[Dict]:
        """
        Get recent confidence log entries.
        """
        db = self.get_db_session()
        try:
            query = db.query(ConfidenceLog)
            
            if not include_pending:
                query = query.filter(ConfidenceLog.outcome.isnot(None))
            
            entries = query.order_by(ConfidenceLog.timestamp.desc()).limit(limit).all()
            
            return [entry.to_dict() for entry in entries]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent entries: {e}")
            raise
        finally:
            db.close()
    
    def cleanup_old_entries(self, days_to_keep: int = 90) -> int:
        """
        Clean up old entries beyond the retention period.
        Returns number of deleted entries.
        """
        db = self.get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            deleted_count = db.query(ConfidenceLog).filter(
                ConfidenceLog.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted_count} old confidence log entries")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up old entries: {e}")
            db.rollback()
            raise
        finally:
            db.close()

# Global service instance
confidence_scoring_service = ConfidenceScoringService() 