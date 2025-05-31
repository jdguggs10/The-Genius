# Step 3 Implementation: Guardrails & Scratchpad Roles

## Overview
This document describes the implementation of Step 3 from the prompt improvement guide: "Introduce Guardrails & Scratchpad Roles"

## What Was Implemented

### 3.1 Guardrails Role (`guardrails@1.0.0.md`)
- **Purpose**: A second system message that enforces constraints and validation rules
- **Placement**: Should be injected AFTER the main system prompt (`base-instructions@1.2.0.md`)
- **Content**: Enforces JSON schema compliance, conversation continuity, and confidence scoring requirements
- **Policy Priority**: Ensures guardrails win over general knowledge when conflicts arise

### 3.2 Assistant Scratchpad (`assistant-scratchpad@1.0.0.md`)
- **Purpose**: Provides structured internal reasoning framework hidden from users
- **Role**: Assistant role message that processes workflow steps internally
- **Benefit**: Leverages Responses API's ability to hide assistant-role messages from users
- **Structure**: Follows the guide's recommendation with search → analyze → answer workflow

## Integration Instructions

### For Backend Implementation
1. **Message Sequence**: When constructing requests to the Responses API:
   ```
   1. System message: base-instructions@1.2.0.md
   2. System message: guardrails@1.0.0.md  
   3. Assistant message: assistant-scratchpad@1.0.0.md
   4. User message: [actual user request]
   ```

2. **Policy Priority**: The guardrails role is placed after base instructions so validation rules take precedence over general guidelines

3. **Hidden Reasoning**: The assistant scratchpad message remains hidden from users but guides the model's internal processing

### Benefits Achieved
- **Separation of Concerns**: Policy (guardrails) separated from workflow (scratchpad)
- **Enhanced Validation**: Explicit JSON schema enforcement
- **Hidden Chain-of-Thought**: Internal reasoning without exposing process to users
- **Consistent Structure**: Standardized approach to request processing

### Testing Considerations
- Verify guardrails prevent invalid JSON responses
- Confirm assistant scratchpad content is not visible to users
- Test that policy rules in guardrails override conflicting general instructions
- Validate that internal reasoning follows the structured workflow

## File Versions
- `guardrails@1.0.0.md`: Initial implementation
- `assistant-scratchpad@1.0.0.md`: Enhanced version of existing assistant workflow template

## Next Steps
Proceed to Step 4 of the guide: "Codify Web-Search Discipline" to further optimize the system. 