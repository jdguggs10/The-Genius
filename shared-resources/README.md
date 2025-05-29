# Shared Resources
# Location for files and content to be used across the entire project

This directory contains files and configurations used across the entire project.

## 📄 Contents

### `prompts/` - Modular Prompt System
**NEW IMPROVED SYSTEM** - Replaces the old `prompts.json` with easier-to-manage individual files.

The new modular prompt system provides:
- **Universal prompts** that apply to all AI requests
- **Sport-specific prompts** for baseball, football, basketball
- **Easy updates** - just edit markdown files directly
- **Systematic organization** - each component in its own file
- **Automatic combination** - system intelligently merges all components

**Structure**:
```
prompts/
├── universal/               # Applied to ALL requests
│   ├── base-instructions.md      # Core AI behavior
│   ├── confidence-guidelines.md  # 0.0-1.0 scoring system  
│   ├── response-format.md        # JSON structure rules
│   └── web-search-guidelines.md  # Search best practices
├── baseball/system-prompt.md     # MLB expertise
├── football/system-prompt.md     # NFL expertise
├── basketball/system-prompt.md   # NBA expertise
└── README.md                     # Full documentation
```

**How to Update Prompts**:
1. **Edit any `.md` file** - changes are immediate, no restart needed
2. **Sport-specific changes**: Edit the relevant sport's `system-prompt.md`
3. **Universal changes**: Edit files in the `universal/` directory
4. **Override everything**: Set `SYSTEM_PROMPT` environment variable

**Usage in API**:
```json
{
  "conversation": [{"role": "user", "content": "Start Mahomes or Allen?"}],
  "prompt_type": "football",  // ← Select sport-specific expertise
  "enable_web_search": true
}
```

**Available Prompt Types**: 
- `default` - General fantasy sports
- `detailed` - Enhanced analysis  
- `football` - NFL-specific
- `baseball` - MLB-specific
- `basketball` - NBA-specific

**Priority Order**:
1. Environment variable (`SYSTEM_PROMPT`) - overrides all
2. Sport-specific + universal files
3. Universal files only
4. Hardcoded fallback

See `prompts/README.md` for complete documentation and examples.

---

### Legacy Files (Deprecated)

~~`prompts.json`~~ - **REPLACED** by the new modular system above. This file may still exist but is no longer used by the application.

---

This modular system makes prompt management **much easier** and more **systematic** than the previous single JSON file approach. You can now update prompts by simply editing markdown files!