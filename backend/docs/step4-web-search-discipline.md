# Step 4: Web Search Discipline Implementation

## Overview

Step 4 of the prompt improvement guide implements **systematic web search discipline** that removes the burden of search decisions from the LLM, saving tokens and improving consistency. Instead of the model deciding whether to search on each request, the backend applies deterministic rules.

## Core Rule Implementation

```
IF (query_is_time_sensitive OR entity_recently_active ≤ 7 days) 
THEN search() 
ELSE skip_search()
```

## Architecture Components

### 1. WebSearchDiscipline Service (`app/services/web_search_discipline.py`)

The core service that implements systematic search decision logic:

```python
from app.services.web_search_discipline import web_search_discipline, SearchDecision

# Make search decision
decision, reasoning = web_search_discipline.should_search(
    user_query="Should I start Josh Allen tonight?",
    conversation_context=conversation_messages,
    user_override=None
)

# decision: SearchDecision.MANDATORY | SearchDecision.SKIP | SearchDecision.BYPASS
# reasoning: Human-readable explanation of the decision
```

### 2. API Integration (`app/main.py`)

Both streaming and non-streaming endpoints now use the search discipline:

```python
# Automatic search discipline (default behavior)
if body.enable_web_search is None:
    search_decision, search_reasoning = web_search_discipline.should_search(
        user_query=latest_message,
        conversation_context=conversation_messages,
        user_override=body.search_override
    )
    enable_web_search_final = search_decision == SearchDecision.MANDATORY

# Manual override (force search on/off)
else:
    enable_web_search_final = body.enable_web_search
```

### 3. Updated Request Model (`app/models.py`)

New fields support the search discipline approach:

```python
class AdviceRequest(BaseModel):
    # ... existing fields ...
    enable_web_search: Optional[bool] = None  # None = use automatic discipline
    search_override: Optional[str] = None     # User commands like "/nosrch"
```

### 4. Updated Prompt Guidelines (`shared-resources/prompts/universal/web-search-guidelines@1.1.0.md`)

The LLM prompt now explains that search decisions are handled automatically, allowing the model to focus on analysis rather than search decisions.

## Search Decision Logic

### Time-Sensitive Triggers (Always Search)
- **Immediate status**: today, tonight, now, current, latest, recent, breaking
- **Injury/availability**: injury, hurt, questionable, doubtful, out, gtd, ruled out
- **Performance trends**: trending, hot, cold, slump, streak, last game, since
- **Weather conditions**: weather, wind, rain, snow, temperature, dome
- **Lineup changes**: starting, bench, snap count, targets, role change
- **Breaking news**: news, update, report, announced, confirmed, trade, waiver
- **Date patterns**: 2024-01-15, Week 15, this Sunday, next game

### Recently Active Entity Triggers (Always Search)
- **Fantasy decisions**: start, sit, lineup, roster, waiver, trade, pickup, drop
- **Analysis requests**: matchup, projection, ranking, advice, play, avoid
- **Player-specific queries**: Proper names, "vs" matchups, performance analysis
- **Daily fantasy**: dfs, prop bet, anytime td, over/under

### Skip Search (Automatic)
- Historical statistics older than current week
- Pure player biography without performance context  
- Established league rules or general strategy
- Theoretical "what if" scenarios without real-time needs

### User Override Commands
- `/nosrch` - Skip search for this query
- `/nosearch` - Skip search for this query  
- `--no-web-search` - Skip search for this query

## Usage Examples

### 1. Basic API Usage

```bash
# Query that will trigger search (time-sensitive)
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "Should I start Josh Allen tonight?"}
    ]
  }'

# Query that will skip search (historical)
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "Who won MVP in 2019?"}
    ]
  }'

# Query with user override (bypass search)
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "Should I start Josh Allen tonight? /nosrch"}
    ]
  }'
```

### 2. Search Discipline Testing

```bash
# Test the search discipline logic
curl -X POST "http://localhost:8000/search-discipline" \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest injury report for Josh Allen"}'

# Test with override
curl -X POST "http://localhost:8000/search-discipline" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest injury report for Josh Allen",
    "search_override": "/nosrch"
  }'
```

### 3. CLI Testing

```bash
# Run example test cases
python backend/test_search_discipline_cli.py

# Test specific query
python backend/test_search_discipline_cli.py --query "Should I start Josh Allen tonight?"

# Interactive mode
python backend/test_search_discipline_cli.py --interactive
```

## Benefits

### 1. Token Savings
- LLM no longer spends tokens deciding whether to search
- Consistent decisions reduce prompt length variations
- Focus on analysis rather than search decision making

### 2. Improved Consistency
- Deterministic rules ensure consistent search behavior
- No variation based on model mood or context length
- Predictable behavior for monitoring and debugging

### 3. Better Performance
- Faster response times (no search decision overhead)
- Reduced API costs from shorter prompts
- More reliable search triggering for time-sensitive queries

### 4. Enhanced Monitoring
- Detailed logging of search decisions and reasoning
- Query classification for analytics
- Metadata tracking for optimization

## Monitoring and Analytics

The system provides extensive logging and analytics:

```python
# Search decision metadata
{
  "tool": "web_search",
  "policy": "mandatory",
  "reasoning": "Time-sensitive query detected: tonight, start",
  "inputs": {
    "recency_days": 7,
    "query_classification": "lineup_decision"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "query_length": 42,
    "has_conversation_context": true,
    "user_override_detected": false
  }
}
```

## Testing

### Unit Tests
Comprehensive test suite in `backend/tests/test_web_search_discipline.py`:

```bash
cd backend
python -m pytest tests/test_web_search_discipline.py -v
```

### Integration Tests
Test the full API integration:

```bash
python -m pytest tests/test_api_integration.py -v
```

### Manual Testing
Use the CLI tool for manual verification:

```bash
python backend/test_search_discipline_cli.py --interactive
```

## Configuration

### Recency Threshold
Configure the recency threshold for "recently active" entities:

```python
# Default: 7 days
discipline = WebSearchDiscipline(recency_threshold_days=7)

# Custom: 14 days  
discipline = WebSearchDiscipline(recency_threshold_days=14)
```

### Environment Variables
No special environment variables required - the system uses the same OpenAI configuration as the main application.

## Migration Notes

### From Previous Version
1. **API Compatibility**: Existing API calls continue to work
2. **Gradual Migration**: Set `enable_web_search: null` to use new discipline
3. **Force Override**: Set `enable_web_search: true/false` to force behavior
4. **Prompt Updates**: Update to use `web-search-guidelines@1.1.0.md`

### Rollback Plan
If issues arise, you can:
1. Set `enable_web_search: true` to force search on all requests
2. Revert prompt files to v1.0.0 versions
3. Deploy previous version of the backend

## Future Enhancements

### Planned Improvements
1. **Entity Database Integration**: Connect to real-time player/team activity feeds
2. **Machine Learning Enhancement**: Learn from search result quality over time
3. **Context-Aware Rules**: More sophisticated conversation context analysis
4. **Performance Optimization**: Cache search decisions for repeated queries

### Extensibility Points
- Custom keyword sets for different sports
- Configurable rule weights and thresholds
- Plugin architecture for custom decision logic
- Integration with external sports data APIs

## Troubleshooting

### Common Issues

**Search not triggering for expected queries**
- Check query classification with the test endpoint
- Verify keywords are in the time_sensitive_keywords set
- Test with the CLI tool to debug logic

**Search triggering for historical queries**
- Review the query for hidden time-sensitive keywords
- Check if player names are triggering active entity detection
- Use override commands to bypass if needed

**User overrides not working**
- Ensure bypass keywords are in the query or search_override field
- Check that keywords match exactly (case-insensitive)
- Verify the override is being passed to the API correctly

### Debug Tools
1. **Test endpoint**: `/search-discipline` for query analysis
2. **CLI tool**: Interactive testing and debugging
3. **Logs**: Detailed search decision logging in application logs
4. **Unit tests**: Verify specific rule behavior

---

This implementation successfully completes Step 4 of the prompt improvement guide, providing systematic web search discipline that saves tokens, improves consistency, and enhances the overall quality of the fantasy sports advice system. 