# Step 5: Confidence Scoring Implementation

This document details the implementation of **Step 5: Calibrate Confidence Scoring** from the prompt improvement guide.

## Overview

Step 5 implements a complete confidence scoring calibration system that:

1. **Logs Ground Truth** - Stores (response, confidence_score, outcome) triples in a database
2. **Weekly Brier Score Pipeline** - Calculates Brier scores and identifies calibration issues  
3. **Auto-tune Phrases** - Automatically adjusts confidence language based on performance

## Components

### 5.1 Log Ground Truth

**Files:**
- `app/models.py` - Database models for confidence logging
- `app/services/confidence_scoring.py` - Core confidence scoring service
- `app/services/response_logger.py` - Response logging integration

**Features:**
- SQLAlchemy database models for confidence logs
- Automatic logging of all API responses with confidence scores
- User feedback collection for ground truth outcomes
- Comprehensive error handling and logging

**Database Schema:**
```sql
CREATE TABLE confidence_logs (
    id INTEGER PRIMARY KEY,
    response_text TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    user_query TEXT NOT NULL,
    conversation_context TEXT,
    model_used VARCHAR(100) NOT NULL,
    web_search_used BOOLEAN NOT NULL,
    outcome BOOLEAN,  -- NULL until feedback received
    timestamp DATETIME NOT NULL,
    feedback_timestamp DATETIME,
    response_id VARCHAR(200) UNIQUE
);
```

### 5.2 Weekly Brier Score Pipeline

**Files:**
- `backend/scripts/weekly_brier_score_pipeline.py` - Main pipeline script
- `.github/workflows/weekly-brier-score.yml` - Automated CI pipeline

**Features:**
- Comprehensive Brier score calculation
- Confidence band calibration analysis
- Model performance breakdown
- Web search impact analysis
- Automated recommendations generation

**Brier Score Calculation:**
```python
brier_score = (1/n) * Σ(predicted_probability - actual_outcome)²
```

**Usage:**
```bash
# Run pipeline manually
python scripts/weekly_brier_score_pipeline.py --days 7 --output report.json

# Run with verbose output
python scripts/weekly_brier_score_pipeline.py --days 14 --verbose
```

### 5.3 Auto-tune Phrases

**Files:**
- `app/services/confidence_phrase_tuner.py` - Phrase tuning service
- `shared-resources/confidence-phrases.json` - Confidence phrase mappings

**Features:**
- Automatic calibration drift detection
- Phrase adjustment based on performance data
- Backup and versioning of phrase changes
- Dry-run mode for testing

**Confidence Bands:**
- `0.9-1.0`: Very High Confidence
- `0.7-0.9`: High Confidence  
- `0.5-0.7`: Moderate Confidence
- `0.3-0.5`: Low Confidence
- `0.1-0.3`: Very Low Confidence

## API Endpoints

### Feedback Submission
```http
POST /feedback
Content-Type: application/json

{
    "response_id": "response_12345",
    "outcome": true,
    "feedback_notes": "Advice was helpful and accurate"
}
```

### Confidence Statistics
```http
GET /confidence/stats?days_back=7
```

Returns:
```json
{
    "brier_score": {
        "brier_score": 0.15,
        "entries_count": 42,
        "accuracy": 0.76,
        "needs_calibration": false
    },
    "distribution": {
        "high": {"count": 15, "accuracy": 0.8},
        "medium": {"count": 20, "accuracy": 0.75}
    }
}
```

### Recent Logs
```http
GET /confidence/recent?limit=20
```

### Brier Score Calculation
```http
GET /confidence/brier-score?days_back=7
```

### Calibration Analysis
```http
GET /confidence/calibration?days_back=30
```

### Auto-tune Control
```http
POST /confidence/auto-tune?days_back=7&dry_run=true
```

## Integration Points

### Response Logging Integration

The system automatically logs confidence data for all responses:

```python
# In main.py streaming endpoint
async def streaming_response_with_logging():
    async for chunk in get_streaming_response(...):
        yield chunk
        
        if chunk.startswith("event: response_complete"):
            # Extract and log final response
            response_logger.log_response(
                advice=final_advice,
                user_query=latest_message,
                conversation_context=conversation_messages,
                model_used=model_to_use,
                web_search_used=enable_web_search_final,
                response_id=openai_response_id
            )
```

### Automated Monitoring

**GitHub Actions Workflow:**
- Runs every Sunday at 6 AM UTC
- Calculates weekly Brier scores
- Runs auto-tuning analysis
- Creates issues for calibration problems
- Generates artifacts with detailed reports

**Monitoring Alerts:**
- Brier score > 0.25 threshold
- Significant calibration drift
- Low accuracy trends

## Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./confidence_logs.db  # Database connection
OPENAI_API_KEY=sk-...                        # Required for analysis
```

### Auto-tune Settings
```json
{
    "auto_tune_settings": {
        "enabled": true,
        "calibration_threshold": 0.1,
        "minimum_samples": 10,
        "update_frequency_days": 7,
        "backup_on_update": true
    }
}
```

## Testing

### Manual Testing
```bash
# Run comprehensive test suite
python backend/test_step5_confidence_scoring.py

# Test weekly pipeline
python backend/scripts/weekly_brier_score_pipeline.py --days 30 --verbose
```

### Test Coverage
- ✅ Confidence logging functionality
- ✅ Outcome feedback system
- ✅ Brier score calculation
- ✅ Calibration analysis
- ✅ Auto-tune phrase system
- ✅ API endpoint integration
- ✅ Weekly pipeline automation

## Monitoring & Alerting

### Key Metrics
1. **Brier Score** - Overall calibration quality (target: < 0.25)
2. **Accuracy by Band** - Confidence band performance
3. **Calibration Error** - Difference between predicted and actual rates
4. **Response Volume** - Number of responses logged per day

### Alert Conditions
- Brier score exceeds 0.25 for 7+ days
- Confidence band calibration error > 0.1
- Overall accuracy drops below 60%
- No feedback received for 14+ days

### Dashboard Metrics
```python
# Example monitoring query
recent_stats = confidence_scoring_service.calculate_brier_score(days_back=7)
if recent_stats['needs_calibration']:
    alert_team(f"Brier score {recent_stats['brier_score']:.3f} exceeds threshold")
```

## Best Practices

### 1. Regular Calibration Reviews
- Run weekly Brier score analysis
- Review auto-tune recommendations
- Monitor confidence band accuracy

### 2. Feedback Collection
- Implement user feedback mechanisms
- Follow up on low-confidence responses
- Track prediction accuracy over time

### 3. Phrase Updates
- Use auto-tune recommendations carefully
- A/B test phrase changes when possible
- Maintain phrase version history

### 4. Database Maintenance
```python
# Clean up old entries (recommended: 90 days)
confidence_scoring_service.cleanup_old_entries(days_to_keep=90)
```

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```python
# Check database URL and permissions
from app.services.confidence_scoring import confidence_scoring_service
confidence_scoring_service.get_db_session()
```

**Missing Dependencies:**
```bash
pip install sqlalchemy pandas scikit-learn
```

**Auto-tune Not Working:**
```python
# Check phrase file permissions and configuration
status = confidence_phrase_tuner.get_calibration_status()
print(f"Auto-tune enabled: {status['auto_tune_enabled']}")
```

**Low Sample Sizes:**
- Increase data collection period
- Lower minimum sample requirements in config
- Use longer analysis windows

### Debug Commands
```bash
# Check recent confidence logs
curl http://localhost:8000/confidence/recent?limit=5

# Get calibration status
curl http://localhost:8000/confidence/phrase-status

# Run dry-run auto-tune
curl -X POST "http://localhost:8000/confidence/auto-tune?dry_run=true"
```

## Performance Considerations

### Database Optimization
- Index on `timestamp` and `response_id` columns
- Consider partitioning for large datasets
- Regular cleanup of old entries

### Memory Usage
- Streaming responses to avoid memory buildup
- Batch processing for large analysis periods
- Lazy loading of conversation contexts

### API Performance
- Cache frequently accessed statistics
- Use background tasks for heavy analysis
- Implement rate limiting on feedback endpoints

## Security

### Data Protection
- Anonymize user queries in logs
- Secure database access credentials
- Regular backup of confidence data

### API Security
- Validate all input parameters
- Implement request rate limiting
- Audit feedback submission logs

## Migration Guide

### From Basic Confidence Scoring
1. Install new dependencies: `pip install -r requirements.txt`
2. Run database migrations: Tables auto-created on first run
3. Update API calls to include response logging
4. Configure auto-tune settings in `confidence-phrases.json`
5. Set up GitHub Actions workflow for automation

### Version Updates
- Backup existing phrase configurations
- Review auto-tune recommendations before applying
- Test in staging environment first
- Monitor Brier scores after changes

## Next Steps

### Enhancements
- [ ] Machine learning-based phrase optimization
- [ ] Real-time confidence adjustment
- [ ] Advanced calibration metrics (reliability diagrams)
- [ ] Integration with A/B testing framework

### Monitoring Improvements
- [ ] Real-time dashboards
- [ ] Slack/email alert integration
- [ ] Custom calibration metrics
- [ ] Trend analysis and forecasting

---

**Implementation Status:** ✅ Complete
**Last Updated:** 2024-01-15
**Guide Version:** 1.0.0 