# **Prompt System Updates for Responses API & SSE Alignment**

## **Overview**

This document outlines the comprehensive updates made to The Genius prompt system to align with OpenAI's Responses API best practices and the SSE (Server-Sent Events) improvements implemented in the application.

## **Key Changes Made**

### **1. Universal Base Instructions Updates**

**File**: `shared-resources/prompts/universal/base-instructions.md`

**Major Changes**:
- ✅ **Added Responses API awareness** - Explicitly mentions being powered by OpenAI's Responses API
- ✅ **Enhanced conversation context handling** - New section on conversation context awareness
- ✅ **Multi-turn conversation guidelines** - Specific instructions for building on previous exchanges
- ✅ **Prioritized information sources** - Conversation context is now the #1 priority
- ✅ **Streaming considerations** - Instructions for smooth streaming without context loss

**Key Additions**:
```markdown
## Conversation Context Awareness
- Remember and reference previous questions and answers
- Build upon earlier analysis and recommendations
- Use pronouns and context clues appropriately
- Maintain consistency across multiple turns

## Multi-Turn Conversation Guidelines
- Reference specific players, teams, or analysis from earlier
- Avoid repeating identical information unless asked
- Build complex analysis across multiple exchanges
- Ask clarifying questions when references are ambiguous
```

### **2. Response Format Guidelines Updates**

**File**: `shared-resources/prompts/universal/response-format.md`

**Major Changes**:
- ✅ **Streaming architecture optimization** - Guidelines specifically for SSE streaming
- ✅ **Conversation context integration** - Instructions for referencing previous exchanges
- ✅ **Enhanced reasoning structure** - Multi-turn conversation reasoning patterns
- ✅ **Web search integration** - How to incorporate real-time findings
- ✅ **Improved examples** - Context-aware recommendation examples

**Key Additions**:
```markdown
## Streaming Considerations
- Ensure JSON is valid when streaming completes
- Structure content to be coherent even if streaming stops mid-response
- Avoid references that require earlier parts of same response

## Conversation Context Integration
- Reference specific players, teams, or scenarios from previous turns
- Build complex analysis across multiple exchanges
- Acknowledge when recommendations change based on new information
```

### **3. Web Search Guidelines Updates**

**File**: `shared-resources/prompts/universal/web-search-guidelines.md`

**Major Changes**:
- ✅ **Responses API integration** - Specific guidance for built-in web search tool
- ✅ **Conversation-aware search strategy** - Search patterns that build on conversation history
- ✅ **Multi-turn search optimization** - How to search for updates to previously discussed players
- ✅ **Quality assessment framework** - Structured approach to evaluating search results
- ✅ **Error handling** - How to handle search failures or conflicts

**Key Additions**:
```markdown
## Search Strategy for Multi-Turn Conversations
1. Build on conversation context - Search for updates to previously discussed players
2. Verify assumptions - Check if earlier analysis still holds
3. Cross-reference findings - Ensure consistency across sources
4. Update recommendations - Adjust previous advice based on new information

## Conversation-Aware Search Triggers
- "Latest news on [player mentioned earlier]"
- "Current injury status" (for previously discussed players)
- Terms like "now," "currently," "latest," "today," "this week"
```

### **4. Confidence Guidelines Updates**

**File**: `shared-resources/prompts/universal/confidence-guidelines.md`

**Major Changes**:
- ✅ **Conversation context adjustments** - How conversation history affects confidence
- ✅ **Web search quality impact** - Confidence adjustments based on search result quality
- ✅ **Streaming considerations** - Confidence scoring that works with SSE streaming
- ✅ **Enhanced examples** - Context-aware confidence scoring examples

**Key Additions**:
```markdown
## Conversation Context Adjustments
### Building on Previous Analysis (+0.1 to +0.2)
- When recommendation reinforces earlier sound reasoning
- When new information confirms previous projections

### Contradicting Previous Analysis (-0.1 to -0.3)
- When new information requires changing earlier recommendations
- When search findings contradict conversation assumptions

## Web Search Quality Impact
### High-Quality Search Results (+0.1 to +0.2)
- Official team sources, verified journalists
- Recent timestamps (last 24-48 hours)
```

### **5. Legacy Prompts.json Updates**

**File**: `shared-resources/prompts.json`

**Major Changes**:
- ✅ **Deprecation notice** - Clear indication that this file is no longer used
- ✅ **Updated content alignment** - Remaining content aligned with new system
- ✅ **Responses API optimizations** - New section with API-specific guidance
- ✅ **Conversation context integration** - All prompts updated for context awareness

**Key Additions**:
```json
{
  "_DEPRECATION_NOTICE": "This file is deprecated...",
  "responses_api_optimizations": {
    "conversation_state": "Use previous_response_id when available",
    "web_search_integration": "Leverage built-in web search tool",
    "streaming_considerations": "Structure responses to be coherent during streaming"
  }
}
```

## **Alignment with SSE Improvements**

### **✅ Conversation Context Management**
- Prompts now explicitly instruct the AI to maintain conversation history
- Guidelines for referencing previous exchanges and building on earlier analysis
- Instructions for handling conversation continuity across SSE streaming

### **✅ Previous Response ID Usage**
- Clear guidance on when and how to use conversation state
- Instructions for building on vs. contradicting previous analysis
- Confidence scoring adjustments based on conversation consistency

### **✅ Web Search Integration**
- Specific guidance for the Responses API built-in web search tool
- Instructions for integrating search findings with conversation context
- Quality assessment framework for search results

### **✅ Streaming Optimization**
- Guidelines for structuring responses that stream coherently
- Instructions for confidence scoring that works with SSE
- Error handling for streaming scenarios

## **Implementation Benefits**

### **1. Improved Conversation Flow**
- AI now maintains context across multiple turns
- Reduces repetitive responses and improves user experience
- Better handling of follow-up questions and pronoun references

### **2. Enhanced Information Quality**
- Real-time web search integration with conversation awareness
- Better confidence scoring based on information quality and context
- Improved handling of conflicting or updated information

### **3. Streaming Optimization**
- Responses structured for smooth SSE delivery
- Coherent partial responses if streaming is interrupted
- Better error handling and recovery

### **4. API Best Practices**
- Full alignment with OpenAI Responses API documentation
- Proper utilization of built-in tools and features
- Optimized for conversation state management

## **Testing Recommendations**

### **Multi-Turn Conversation Tests**
1. **Context Continuity**: Ask about a player, then reference "him" or "his stats"
2. **Information Updates**: Ask about a player, then ask for "latest news" on same player
3. **Recommendation Changes**: Test scenarios where new information changes previous advice
4. **Complex Analysis**: Build analysis across 3+ conversation turns

### **Web Search Integration Tests**
1. **Real-time Updates**: Ask about injury status for current day
2. **Weather Queries**: Ask about game conditions for upcoming games
3. **Breaking News**: Test handling of conflicting information sources
4. **Search Quality**: Verify confidence adjustments based on search results

### **Streaming Performance Tests**
1. **Partial Response Coherence**: Test if responses make sense when streaming stops mid-way
2. **Confidence Accuracy**: Verify confidence scores reflect actual response quality
3. **Error Recovery**: Test graceful handling of search failures or API issues

## **Future Considerations**

### **Sport-Specific Enhancements**
- Consider updating sport-specific prompts with similar conversation awareness
- Add sport-specific web search patterns (e.g., baseball weather impact)
- Enhance position-specific analysis patterns

### **Advanced Features**
- User preference learning across conversations
- Long-term conversation memory (beyond single sessions)
- Multi-user conversation handling for group chats

## **Conclusion**

These prompt system updates ensure full alignment with:
- ✅ **OpenAI Responses API best practices**
- ✅ **SSE streaming improvements implemented in the application**
- ✅ **Conversation context management requirements**
- ✅ **Real-time web search integration**

The updated system provides a significantly improved user experience with proper conversation continuity, enhanced information quality, and optimized streaming performance. 