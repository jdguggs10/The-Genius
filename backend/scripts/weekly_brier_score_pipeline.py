#!/usr/bin/env python3
"""
Step 5.2: Weekly Brier Score Pipeline
Implements the weekly confidence scoring analysis as per prompt improvement guide.

Usage:
    python scripts/weekly_brier_score_pipeline.py [--days 7] [--output report.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import pandas as pd
    from sklearn.metrics import brier_score_loss
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Warning: pandas and sklearn not available. Using basic Brier score calculation.")
    SKLEARN_AVAILABLE = False

from app.services.confidence_scoring import confidence_scoring_service
from app.models import ConfidenceLog

def calculate_brier_score_manual(confidence_scores, outcomes):
    """
    Manual Brier score calculation when sklearn is not available.
    Brier score = (1/n) * Σ(predicted_probability - actual_outcome)²
    """
    if len(confidence_scores) != len(outcomes):
        raise ValueError("Confidence scores and outcomes must have the same length")
    
    if len(confidence_scores) == 0:
        return None
    
    total_score = sum(
        (conf - outcome) ** 2 
        for conf, outcome in zip(confidence_scores, outcomes)
    )
    
    return total_score / len(confidence_scores)

def generate_brier_report(days_back: int = 7) -> dict:
    """Generate comprehensive Brier score report."""
    print(f"🎯 Generating Brier Score Report for last {days_back} days...")
    
    # Get basic Brier score from service
    basic_stats = confidence_scoring_service.calculate_brier_score(days_back)
    
    if basic_stats["entries_count"] == 0:
        return {
            "status": "no_data",
            "message": f"No entries with outcomes found for the last {days_back} days",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Get detailed distribution
    distribution = confidence_scoring_service.get_confidence_distribution(days_back)
    
    # Enhanced analysis if we have the data
    db = confidence_scoring_service.get_db_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        entries = db.query(ConfidenceLog).filter(
            ConfidenceLog.outcome.isnot(None),
            ConfidenceLog.timestamp >= cutoff_date
        ).all()
        
        if entries:
            confidence_scores = [entry.confidence_score for entry in entries]
            outcomes = [1.0 if entry.outcome else 0.0 for entry in entries]
            
            # Calculate Brier score using sklearn if available
            if SKLEARN_AVAILABLE:
                sklearn_brier = brier_score_loss(outcomes, confidence_scores)
                print(f"📊 Sklearn Brier Score: {sklearn_brier:.4f}")
            else:
                sklearn_brier = calculate_brier_score_manual(confidence_scores, outcomes)
                print(f"📊 Manual Brier Score: {sklearn_brier:.4f}")
            
            # Calibration analysis
            calibration_bands = analyze_calibration(entries)
            
            # Model performance breakdown
            model_performance = analyze_by_model(entries)
            
            # Search vs no-search performance
            search_performance = analyze_by_search_usage(entries)
            
        else:
            sklearn_brier = None
            calibration_bands = None
            model_performance = None
            search_performance = None
            
    finally:
        db.close()
    
    # Compile comprehensive report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "period_days": days_back,
        "summary": {
            "brier_score": basic_stats["brier_score"],
            "sklearn_brier_score": sklearn_brier,
            "entries_analyzed": basic_stats["entries_count"],
            "accuracy": basic_stats["accuracy"],
            "avg_confidence": basic_stats["avg_confidence"],
            "needs_calibration": basic_stats["needs_calibration"],
            "calibration_threshold": 0.25  # From guide
        },
        "confidence_distribution": distribution,
        "calibration_analysis": calibration_bands,
        "model_performance": model_performance,
        "search_impact": search_performance,
        "recommendations": generate_recommendations(basic_stats, calibration_bands)
    }
    
    return report

def analyze_calibration(entries) -> dict:
    """Analyze calibration across confidence bands."""
    bands = [
        (0.0, 0.5, "low_confidence"),
        (0.5, 0.7, "medium_confidence"), 
        (0.7, 0.9, "high_confidence"),
        (0.9, 1.0, "very_high_confidence")
    ]
    
    calibration = {}
    for min_conf, max_conf, band_name in bands:
        band_entries = [
            entry for entry in entries
            if min_conf <= entry.confidence_score < max_conf
        ]
        
        if band_entries:
            predicted_prob = sum(entry.confidence_score for entry in band_entries) / len(band_entries)
            actual_rate = sum(1 for entry in band_entries if entry.outcome) / len(band_entries)
            calibration_error = abs(predicted_prob - actual_rate)
            
            calibration[band_name] = {
                "count": len(band_entries),
                "avg_predicted_prob": predicted_prob,
                "actual_success_rate": actual_rate,
                "calibration_error": calibration_error,
                "is_well_calibrated": calibration_error < 0.1,
                "range": f"{min_conf:.1f}-{max_conf:.1f}"
            }
    
    return calibration

def analyze_by_model(entries) -> dict:
    """Analyze performance breakdown by model."""
    models = {}
    for entry in entries:
        model = entry.model_used
        if model not in models:
            models[model] = []
        models[model].append(entry)
    
    model_stats = {}
    for model, model_entries in models.items():
        if len(model_entries) > 0:
            confidence_scores = [entry.confidence_score for entry in model_entries]
            outcomes = [1.0 if entry.outcome else 0.0 for entry in model_entries]
            
            brier_score = calculate_brier_score_manual(confidence_scores, outcomes)
            accuracy = sum(outcomes) / len(outcomes)
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            model_stats[model] = {
                "entries": len(model_entries),
                "brier_score": brier_score,
                "accuracy": accuracy,
                "avg_confidence": avg_confidence
            }
    
    return model_stats

def analyze_by_search_usage(entries) -> dict:
    """Analyze performance difference between web search enabled/disabled."""
    with_search = [entry for entry in entries if entry.web_search_used]
    without_search = [entry for entry in entries if not entry.web_search_used]
    
    def calc_stats(entry_list):
        if not entry_list:
            return None
        
        confidence_scores = [entry.confidence_score for entry in entry_list]
        outcomes = [1.0 if entry.outcome else 0.0 for entry in entry_list]
        
        return {
            "entries": len(entry_list),
            "brier_score": calculate_brier_score_manual(confidence_scores, outcomes),
            "accuracy": sum(outcomes) / len(outcomes),
            "avg_confidence": sum(confidence_scores) / len(confidence_scores)
        }
    
    return {
        "with_search": calc_stats(with_search),
        "without_search": calc_stats(without_search)
    }

def generate_recommendations(basic_stats, calibration_analysis) -> list:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    brier_score = basic_stats["brier_score"]
    
    if brier_score > 0.25:
        recommendations.append({
            "priority": "high",
            "action": "tighten_confidence_rubric",
            "description": f"Brier score {brier_score:.3f} exceeds 0.25 threshold. Require stricter language for 0.9+ confidence band.",
            "implementation": "Update confidence-guidelines@1.0.0.md to require stronger evidence for high confidence ratings"
        })
    
    if calibration_analysis:
        for band, stats in calibration_analysis.items():
            if not stats.get("is_well_calibrated", True) and stats["count"] >= 5:
                recommendations.append({
                    "priority": "medium",
                    "action": "calibrate_confidence_band",
                    "description": f"{band} band shows calibration error of {stats['calibration_error']:.3f}",
                    "implementation": f"Adjust confidence scoring guidelines for {stats['range']} range"
                })
    
    if basic_stats["accuracy"] < 0.6:
        recommendations.append({
            "priority": "high", 
            "action": "review_prediction_quality",
            "description": f"Overall accuracy {basic_stats['accuracy']:.1%} is below acceptable threshold",
            "implementation": "Review recent incorrect predictions to identify systematic issues"
        })
    
    return recommendations

def main():
    parser = argparse.ArgumentParser(description="Weekly Brier Score Pipeline")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze (default: 7)")
    parser.add_argument("--output", type=str, help="Output file for JSON report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🎯 Step 5.2: Weekly Brier Score Pipeline")
    print("=" * 50)
    
    try:
        report = generate_brier_report(args.days)
        
        # Print summary
        if report.get("status") == "no_data":
            print(f"❌ {report['message']}")
            return
        
        summary = report["summary"]
        print(f"📊 Brier Score: {summary['brier_score']:.4f}")
        print(f"📈 Accuracy: {summary['accuracy']:.1%}")
        print(f"🎯 Avg Confidence: {summary['avg_confidence']:.3f}")
        print(f"📋 Entries Analyzed: {summary['entries_analyzed']}")
        
        if summary["needs_calibration"]:
            print("⚠️  CALIBRATION NEEDED: Brier score exceeds 0.25 threshold")
        else:
            print("✅ Calibration within acceptable range")
        
        # Show key recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n🔧 Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"  {rec['priority'].upper()}: {rec['description']}")
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Full report saved to: {args.output}")
        
        if args.verbose:
            print("\n📋 Full Report:")
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 