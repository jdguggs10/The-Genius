# Modular Prompt System

> **Easy-to-update, systematic prompt management for The Genius AI**

This system replaces the old single JSON file with a modular approach that makes it much easier to update and maintain AI prompts across all sports and use cases.

## 🗂️ **File Structure**

```
shared-resources/prompts/
├── universal/                    # Apply to ALL requests
│   ├── base-instructions.md      # Core AI personality and goals
│   ├── confidence-guidelines.md  # How to score confidence (0.0-1.0)
│   ├── response-format.md        # JSON structure requirements
│   └── web-search-guidelines.md  # When and how to search
│
├── baseball/                     # Baseball-specific prompts
│   └── system-prompt.md          # MLB expertise and considerations
│
├── football/                     # Football-specific prompts
│   └── system-prompt.md          # NFL expertise and considerations
│
├── basketball/                   # Basketball-specific prompts
│   └── system-prompt.md          # NBA expertise and considerations
│
├── STEP_1_COMPLETION_SUMMARY.md  # ✅ Prompt versioning & CI/CD implementation
├── STEP_2_COMPLETION_SUMMARY.md  # ✅ Slim system prompt architecture 
├── STEP_3_IMPLEMENTATION.md      # ✅ Guardrails & scratchpad roles
├── STEP_4_COMPLETION_SUMMARY.md  # ✅ Web search discipline automation
├── STEP_5_COMPLETION_SUMMARY.md  # ✅ Confidence scoring calibration
└── README.md                     # This documentation
```

## 🎯 **How It Works**

### 1. **Universal Prompts** (Always Applied)
Every AI request automatically includes:
- **Base Instructions**: Core AI personality and responsibilities
- **Confidence Guidelines**: Standardized 0.0-1.0 scoring system
- **Response Format**: JSON structure requirements
- **Web Search Guidelines**: How to use web search effectively (when enabled)

### 2. **Sport-Specific Prompts** (When Selected)
When you choose a sport type, it adds specialized knowledge:
- **Football**: NFL stats, weather impact, game scripts
- **Baseball**: Pitcher matchups, park factors, weather
- **Basketball**: Usage rates, pace, back-to-backs

### 3. **Intelligent Combination**
The system automatically combines:
```
Universal Base Instructions
+ Sport-Specific Expertise  
+ Confidence Guidelines
+ Response Format Rules
+ Web Search Instructions (if enabled)
+ User's Question
= Complete AI Prompt
```

## 🚀 **How to Update Prompts**

### **Quick Updates** (Most Common)
1. **Edit any `.md` file directly** - changes take effect immediately
2. **No server restart needed** - files are loaded dynamically
3. **Version control friendly** - each file can be tracked separately

### **Examples**:

**Make football analysis more detailed**:
```bash
# Edit this file:
shared-resources/prompts/football/system-prompt.md

# Add new sections like:
## Weather Impact Analysis
Consider temperature, wind, precipitation effects on passing vs. rushing games...
```

**Update confidence scoring**:
```bash
# Edit this file:
shared-resources/prompts/universal/confidence-guidelines.md

# Modify the 0.9-1.0 section to be more strict...
```

**Change AI personality**:
```bash
# Edit this file:
shared-resources/prompts/universal/base-instructions.md

# Update the core responsibilities or tone...
```

## 📊 **Usage in Code**

### **API Requests**
```json
{
  "conversation": [{"role": "user", "content": "Start Josh Allen or Mahomes?"}],
  "prompt_type": "football",
  "enable_web_search": true
}
```

### **Available Prompt Types**
- `"default"` - General fantasy sports (universal only)
- `"detailed"` - Enhanced general analysis 
- `"football"` - NFL-specific expertise
- `"baseball"` - MLB-specific expertise
- `"basketball"` - NBA-specific expertise

### **Environment Override**
```bash
# In backend/.env file:
SYSTEM_PROMPT="Your custom system prompt that overrides everything"
```

## 🔧 **Advanced Usage**

### **Adding New Sports**
1. Create new directory: `shared-resources/prompts/hockey/`
2. Add `system-prompt.md` with hockey expertise
3. Update `backend/app/models.py` to include `"hockey"` in the Literal type
4. It automatically becomes available!

### **Adding New Universal Components**
1. Create new file in `universal/` directory
2. Update `prompt_loader.py` to load and use it
3. All requests will include the new component

### **Testing Prompts**
```python
# In Python console:
from app.services.prompt_loader import prompt_loader

# Test different prompt types
print(prompt_loader.get_system_prompt("football"))
print(prompt_loader.build_full_prompt("Test question", "System prompt", {}))

# Clear cache to reload files during development
prompt_loader.clear_cache()
```

## ✅ **Benefits of This System**

1. **Easy Updates**: Edit markdown files, changes are immediate
2. **Sport-Specific**: Tailored expertise for each sport
3. **Consistent Base**: Universal guidelines applied everywhere  
4. **Version Control**: Each file tracked separately
5. **Team Collaboration**: Different people can work on different sports
6. **A/B Testing**: Easy to test different prompt variations
7. **Environment Flexibility**: Override with environment variables

## 🚨 **Priority Order**

The system uses this priority when building prompts:

1. **Environment Variable** (`SYSTEM_PROMPT`) - Overrides everything
2. **Sport-Specific Files** + Universal Components
3. **Default Universal Components Only**
4. **Hardcoded Fallback** (last resort)

This ensures you always have working prompts, even if files are missing!

## 🤖 AI Reviewer Notes

For AI agents reviewing the codebase, especially concerning how prompts are constructed and influence AI behavior, these points are key:

-   **Source of Truth for AI Persona**: These markdown files within the `shared-resources/prompts/` directory are the direct source of truth for defining the AI's persona, core instructions, response formatting, and sport-specific knowledge.
-   **Backend Interpreter (`prompt_loader.py`)**: The Python script `backend/app/services/prompt_loader.py` is the component responsible for reading these markdown files, combining them based on the requested `prompt_type`, and caching the results. Understanding its logic is crucial to understanding how the final system prompt is assembled.
-   **Direct Impact of Changes**: Any modifications to these `.md` files will directly affect the system prompts used by the AI, and consequently, its responses. The `prompt_loader.py` is designed to pick up these changes dynamically (often without a server restart).
-   **Combination Logic (Universal + Sport-Specific)**: A core feature is the combination of universal prompts (from `prompts/universal/`) with sport-specific prompts (e.g., from `prompts/football/`). The AI reviewer should pay attention to how these are layered to create contextually relevant system prompts.
-   **Context from Parent README**: The `README.md` file located in the parent `shared-resources/` directory provides additional context on how this modular prompt system fits into the broader project and how it's invoked by the backend.
-   **`prompt_type` in API Calls**: The selection of which sport-specific prompts to apply is typically determined by a `prompt_type` parameter sent in API requests to the backend. This is a key mechanism for tailoring the AI's expertise.

## 📋 **Implementation Progress**

The prompt engineering improvements follow a systematic approach outlined in the prompt improvement guide:

- **✅ Step 1: Treat Prompts as Code** - Semantic versioning, CI linting, unit tests
- **✅ Step 2: Slim the System Prompt** - Separated immutable policy from workflow logic  
- **✅ Step 3: Guardrails & Scratchpad** - Added validation rules and hidden reasoning
- **✅ Step 4: Web Search Discipline** - Automated search decisions with systematic rules
- **✅ Step 5: Confidence Calibration** - Brier score analysis and automatic phrase tuning

Each step summary contains detailed implementation notes, verification results, and architectural benefits achieved.