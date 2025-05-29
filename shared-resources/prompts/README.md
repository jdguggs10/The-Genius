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