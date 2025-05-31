"""
Step 5.3: Auto-tune Phrases Service
Implements automatic confidence phrase calibration as per prompt improvement guide.
"""

import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.services.confidence_scoring import confidence_scoring_service

logger = logging.getLogger(__name__)

class ConfidencePhraseTuner:
    """
    Service for automatically tuning confidence phrases based on calibration data.
    Implements Step 5.3 from the prompt improvement guide.
    """
    
    def __init__(self, phrases_file_path: Optional[str] = None):
        """Initialize the confidence phrase tuner."""
        if phrases_file_path is None:
            # Default to shared-resources/confidence-phrases.json
            self.phrases_file_path = Path(__file__).parent.parent.parent.parent / "shared-resources" / "confidence-phrases.json"
        else:
            self.phrases_file_path = Path(phrases_file_path)
        
        self.phrases_data = self._load_phrases()
        logger.info(f"Confidence phrase tuner initialized with file: {self.phrases_file_path}")
    
    def _load_phrases(self) -> Dict:
        """Load confidence phrases from JSON file."""
        try:
            with open(self.phrases_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Phrases file not found: {self.phrases_file_path}")
            return self._create_default_phrases()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in phrases file: {e}")
            return self._create_default_phrases()
    
    def _create_default_phrases(self) -> Dict:
        """Create default phrases structure if file is missing."""
        return {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat(),
            "confidence_bands": {},
            "auto_tune_settings": {
                "enabled": True,
                "calibration_threshold": 0.1,
                "minimum_samples": 10,
                "update_frequency_days": 7,
                "backup_on_update": True
            },
            "calibration_history": [],
            "usage_statistics": {}
        }
    
    def _save_phrases(self, backup: bool = True) -> bool:
        """Save phrases data to file with optional backup."""
        try:
            if backup and self.phrases_file_path.exists():
                # Create backup
                backup_path = self.phrases_file_path.with_suffix(
                    f'.backup.{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
                )
                shutil.copy2(self.phrases_file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Update timestamp
            self.phrases_data["last_updated"] = datetime.utcnow().isoformat()
            
            # Save updated phrases
            with open(self.phrases_file_path, 'w') as f:
                json.dump(self.phrases_data, f, indent=2)
            
            logger.info(f"Updated phrases file: {self.phrases_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving phrases file: {e}")
            return False
    
    def get_phrase_for_confidence(self, confidence_score: float) -> Optional[str]:
        """Get an appropriate phrase for a given confidence score."""
        for band_key, band_data in self.phrases_data.get("confidence_bands", {}).items():
            range_min, range_max = band_data["range"]
            if range_min <= confidence_score < range_max:
                phrases = band_data.get("phrases", [])
                if phrases:
                    # For now, return the first phrase. Could implement rotation/selection logic
                    return phrases[0]
        
        # Fallback
        return None
    
    def analyze_calibration_drift(self, days_back: int = 7) -> Dict:
        """
        Analyze calibration drift for each confidence band.
        Returns bands that need recalibration.
        """
        logger.info(f"Analyzing calibration drift for last {days_back} days")
        
        # Get confidence distribution from scoring service
        distribution = confidence_scoring_service.get_confidence_distribution(days_back)
        
        if "distribution" not in distribution:
            return {"message": "No calibration data available", "bands_needing_adjustment": []}
        
        bands_needing_adjustment = []
        analysis_results = {}
        
        for band_name, stats in distribution["distribution"].items():
            if stats["count"] == 0 or stats["accuracy"] is None:
                continue
            
            # Map band names to our phrase bands
            phrase_band_key = self._map_distribution_to_phrase_band(band_name)
            if not phrase_band_key:
                continue
            
            phrase_band = self.phrases_data["confidence_bands"].get(phrase_band_key, {})
            calibration_target = phrase_band.get("calibration_target", 0.5)
            
            # Calculate calibration error
            actual_accuracy = stats["accuracy"]
            calibration_error = abs(actual_accuracy - calibration_target)
            
            calibration_threshold = self.phrases_data["auto_tune_settings"]["calibration_threshold"]
            minimum_samples = self.phrases_data["auto_tune_settings"]["minimum_samples"]
            
            needs_adjustment = (
                calibration_error > calibration_threshold and 
                stats["count"] >= minimum_samples
            )
            
            analysis_results[band_name] = {
                "phrase_band_key": phrase_band_key,
                "actual_accuracy": actual_accuracy,
                "target_accuracy": calibration_target,
                "calibration_error": calibration_error,
                "sample_count": stats["count"],
                "needs_adjustment": needs_adjustment,
                "adjustment_direction": "tighten" if actual_accuracy < calibration_target else "loosen"
            }
            
            if needs_adjustment:
                bands_needing_adjustment.append({
                    "band": band_name,
                    "phrase_band": phrase_band_key,
                    "error": calibration_error,
                    "direction": "tighten" if actual_accuracy < calibration_target else "loosen",
                    "samples": stats["count"]
                })
        
        return {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "period_days": days_back,
            "analysis_results": analysis_results,
            "bands_needing_adjustment": bands_needing_adjustment,
            "total_bands_analyzed": len(analysis_results),
            "calibration_threshold": calibration_threshold
        }
    
    def _map_distribution_to_phrase_band(self, distribution_band: str) -> Optional[str]:
        """Map distribution band names to phrase band keys."""
        mapping = {
            "very_high": "0.9-1.0",
            "high": "0.7-0.9", 
            "medium": "0.5-0.7",
            "low": "0.3-0.5"
        }
        return mapping.get(distribution_band)
    
    def auto_tune_phrases(self, days_back: int = 7, dry_run: bool = False) -> Dict:
        """
        Automatically tune phrases based on calibration analysis.
        Returns tuning results and actions taken.
        """
        if not self.phrases_data["auto_tune_settings"]["enabled"]:
            return {"status": "disabled", "message": "Auto-tuning is disabled"}
        
        logger.info(f"Starting auto-tune process (dry_run={dry_run})")
        
        # Analyze calibration drift
        analysis = self.analyze_calibration_drift(days_back)
        
        if not analysis["bands_needing_adjustment"]:
            return {
                "status": "no_action_needed",
                "message": "All bands are well calibrated",
                "analysis": analysis
            }
        
        actions_taken = []
        phrases_updated = 0
        
        for band_adjustment in analysis["bands_needing_adjustment"]:
            band_key = band_adjustment["phrase_band"]
            direction = band_adjustment["direction"]
            error = band_adjustment["error"]
            
            if band_key not in self.phrases_data["confidence_bands"]:
                continue
            
            # Generate updated phrases based on calibration needs
            updated_phrases = self._generate_adjusted_phrases(band_key, direction, error)
            
            if updated_phrases:
                if not dry_run:
                    # Update the phrases
                    self.phrases_data["confidence_bands"][band_key]["phrases"] = updated_phrases
                    self.phrases_data["confidence_bands"][band_key]["last_calibrated"] = datetime.utcnow().isoformat()
                    phrases_updated += 1
                
                actions_taken.append({
                    "band": band_key,
                    "direction": direction,
                    "calibration_error": error,
                    "old_phrases": self.phrases_data["confidence_bands"][band_key]["phrases"],
                    "new_phrases": updated_phrases,
                    "applied": not dry_run
                })
        
        # Record calibration event
        calibration_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "period_analyzed": days_back,
            "bands_adjusted": len(actions_taken),
            "actions": actions_taken,
            "dry_run": dry_run
        }
        
        if not dry_run and actions_taken:
            # Save updated phrases
            self.phrases_data["calibration_history"].append(calibration_record)
            success = self._save_phrases(
                backup=self.phrases_data["auto_tune_settings"]["backup_on_update"]
            )
            
            if success:
                logger.info(f"Auto-tuning completed: {phrases_updated} bands updated")
            else:
                logger.error("Failed to save updated phrases")
                return {"status": "error", "message": "Failed to save updated phrases"}
        
        return {
            "status": "completed",
            "dry_run": dry_run,
            "bands_adjusted": len(actions_taken),
            "phrases_updated": phrases_updated,
            "actions_taken": actions_taken,
            "calibration_record": calibration_record,
            "analysis": analysis
        }
    
    def _generate_adjusted_phrases(self, band_key: str, direction: str, error: float) -> List[str]:
        """
        Generate adjusted phrases for a confidence band.
        This is a simplified implementation - in production, this could use
        more sophisticated NLP techniques.
        """
        band_data = self.phrases_data["confidence_bands"].get(band_key, {})
        current_phrases = band_data.get("phrases", [])
        
        if direction == "tighten":
            # Need more conservative/uncertain language
            adjustments = {
                "I'm very confident": "I believe",
                "This is a strong recommendation": "This is a solid recommendation",
                "I highly recommend": "I recommend",
                "Strong evidence supports": "Good evidence supports",
                "I recommend": "I lean towards",
                "This is a solid choice": "This seems like a good choice",
                "I'm confident": "I think",
                "Strong indicators": "Indicators"
            }
        else:  # direction == "loosen"
            # Need more confident language
            adjustments = {
                "I think": "I'm confident",
                "I lean towards": "I recommend",
                "This seems like": "This is",
                "Moderate evidence": "Strong evidence",
                "I believe": "I'm confident",
                "Good evidence": "Strong evidence"
            }
        
        # Apply adjustments
        adjusted_phrases = []
        for phrase in current_phrases:
            adjusted_phrase = phrase
            for old_part, new_part in adjustments.items():
                if old_part in phrase:
                    adjusted_phrase = phrase.replace(old_part, new_part)
                    break
            adjusted_phrases.append(adjusted_phrase)
        
        return adjusted_phrases
    
    def get_calibration_status(self) -> Dict:
        """Get current calibration status and history."""
        return {
            "phrases_file": str(self.phrases_file_path),
            "version": self.phrases_data.get("version", "unknown"),
            "last_updated": self.phrases_data.get("last_updated"),
            "auto_tune_enabled": self.phrases_data["auto_tune_settings"]["enabled"],
            "calibration_threshold": self.phrases_data["auto_tune_settings"]["calibration_threshold"],
            "total_bands": len(self.phrases_data.get("confidence_bands", {})),
            "calibration_history_count": len(self.phrases_data.get("calibration_history", [])),
            "last_calibration": (
                self.phrases_data["calibration_history"][-1]["timestamp"] 
                if self.phrases_data.get("calibration_history") else None
            )
        }
    
    def manual_phrase_update(self, band_key: str, new_phrases: List[str]) -> bool:
        """Manually update phrases for a specific band."""
        if band_key not in self.phrases_data["confidence_bands"]:
            logger.error(f"Band key not found: {band_key}")
            return False
        
        try:
            old_phrases = self.phrases_data["confidence_bands"][band_key]["phrases"]
            self.phrases_data["confidence_bands"][band_key]["phrases"] = new_phrases
            self.phrases_data["confidence_bands"][band_key]["last_calibrated"] = datetime.utcnow().isoformat()
            
            # Record manual update
            manual_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "manual_update",
                "band": band_key,
                "old_phrases": old_phrases,
                "new_phrases": new_phrases
            }
            self.phrases_data["calibration_history"].append(manual_record)
            
            success = self._save_phrases(backup=True)
            if success:
                logger.info(f"Manually updated phrases for band: {band_key}")
            return success
            
        except Exception as e:
            logger.error(f"Error in manual phrase update: {e}")
            return False

# Global service instance
confidence_phrase_tuner = ConfidencePhraseTuner() 