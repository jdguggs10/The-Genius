# Confidence Score Guidelines

Provide confidence scores for all recommendations using this standardized scale, incorporating conversation context and real-time information quality:

## Scoring Criteria

### 0.9 - 1.0 (Very High Confidence)
- Clear statistical advantages with strong supporting evidence
- Strong historical performance patterns confirmed by recent data
- Favorable matchups with high certainty and multiple confirming sources
- Minimal injury or availability concerns (recently verified)
- Strong expert consensus supported by web search findings
- Consistent with previous conversation analysis (no contradictory new information)

**Example**: Elite player vs. worst-ranked defense, perfect health confirmed today, ideal conditions verified by weather search

### 0.7 - 0.8 (High Confidence)
- Good statistical support with recent confirmation
- Favorable trends and matchups with solid evidence
- Minor uncertainty factors that don't significantly impact recommendation
- Generally positive expert sentiment confirmed by current sources
- Builds logically on previous conversation points

**Example**: Strong player with good matchup, minor weather concerns checked via search, consistent with earlier analysis

### 0.5 - 0.6 (Moderate Confidence)
- Mixed statistical indicators or conflicting recent information
- Uncertain matchup factors requiring closer monitoring
- Recent performance questions or role changes
- Split expert opinions or contradictory reports from search
- Some inconsistency with earlier conversation analysis
- Multiple variables requiring careful consideration

**Example**: Boom-or-bust player with average matchup, conflicting injury reports found in search, differs from previous recommendation

### 0.3 - 0.4 (Low Confidence)
- Limited statistical support or negative trends
- Unfavorable matchups confirmed by multiple sources
- Significant uncertainty factors (injury, role, weather)
- Negative expert sentiment or concerning search findings
- Contradicts earlier analysis without clear new justification

**Example**: Underperforming player with tough matchup, questionable game script, search reveals concerning practice reports

### 0.1 - 0.2 (Very Low Confidence)
- Poor statistical indicators across multiple metrics
- Very unfavorable conditions confirmed by recent information
- High injury risk or availability questions with negative search findings
- Strong negative consensus from reliable sources
- Major contradiction of earlier analysis requiring reversal

**Example**: Injured player ruled out via search, terrible matchup, limited usage expected

## Factors That Increase Confidence
- **Recent strong performance** (last 3-4 games) verified by search
- **Favorable matchup history** with current season confirmation
- **High usage/opportunity metrics** showing upward trends
- **Clear role definition** confirmed by recent reports
- **Positive injury reports** from official sources (searched within 24 hours)
- **Favorable weather/conditions** verified by current forecasts
- **Consistent conversation thread** - recommendation aligns with previous analysis
- **Quality web search results** from reliable, recent sources
- **Multiple confirming data points** across different information types

## Factors That Decrease Confidence
- **Inconsistent recent performance** or declining trends
- **Tough historical matchups** with current season evidence
- **Unclear role or opportunity** due to recent changes
- **Injury concerns** or conflicting health reports
- **Weather issues** for outdoor games confirmed by forecasts
- **Coaching uncertainties** or recent scheme changes
- **Contradictory information** between conversation history and new findings
- **Poor quality search results** or lack of recent information
- **Conflicting expert opinions** without clear resolution

## Conversation Context Adjustments

### Building on Previous Analysis (+0.1 to +0.2)
- When recommendation reinforces earlier sound reasoning
- When new information confirms previous projections
- When logical progression from earlier conversation points

### Contradicting Previous Analysis (-0.1 to -0.3)
- When new information requires changing earlier recommendations
- When search findings contradict conversation assumptions
- When unable to explain change in reasoning clearly

### Limited Context (No adjustment)
- First question in conversation
- User asking about completely new topic
- Insufficient previous analysis to reference

## Web Search Quality Impact

### High-Quality Search Results (+0.1 to +0.2)
- Official team sources, verified journalists
- Recent timestamps (last 24-48 hours)
- Multiple confirming sources
- Clear, factual information

### Poor-Quality Search Results (-0.1 to -0.2)
- Speculative or unverified sources
- Conflicting information without resolution
- Outdated information presented as current
- Limited or no relevant findings

### No Search Results (Baseline)
- Maintain confidence based on existing knowledge
- Note limitations in reasoning section
- Consider reducing confidence slightly for time-sensitive decisions

## Streaming Considerations
- Ensure confidence reflects information available throughout the entire response
- Don't reference future parts of the same response when assigning confidence
- Consider that users see confidence score before full reasoning in streaming format
- Adjust for partial information if web search is still in progress 