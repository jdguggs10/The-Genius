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

## 🤖 AI Reviewer Notes

For AI agents reviewing the codebase, particularly how prompts influence AI behavior, these points are crucial:

-   **Centralized Prompt Management**: The `shared-resources/prompts/` subdirectory is the definitive location for all markdown-based prompt components that define the AI's personality, response structure, and task-specific instructions (e.g., by sport).
-   **Backend Prompt Loading Logic**: The backend module responsible for loading, combining, and caching these prompts is `backend/app/services/prompt_loader.py`. Understanding this script is key to seeing how the individual `.md` files are assembled into the final system prompt sent to the LLM.
-   **`prompt_type` Parameter**: When clients (web app, iOS app) make requests to the backend API, they can specify a `prompt_type` (e.g., "football", "baseball", "default"). This parameter dictates which set of sport-specific prompts are combined with the universal prompts by the `prompt_loader.py`.
-   **Prompt Loading Priority**: The `prompt_loader.py` observes a specific priority order when constructing the final system prompt:
    1.  An environment variable (`SYSTEM_PROMPT` on the backend) can override all file-based prompts.
    2.  If a `prompt_type` is specified and corresponding sport-specific files exist (e.g., `prompts/football/system-prompt.md`), these are loaded along with all files in `prompts/universal/`.
    3.  If the `prompt_type` is "default" or no specific sport files are found, only the files in `prompts/universal/` are loaded.
    4.  A hardcoded fallback prompt within `prompt_loader.py` is used if no files can be loaded and no environment variable is set.
-   **Dynamic Updates**: Changes to the `.md` prompt files in the `prompts/` directory are typically picked up dynamically by the `prompt_loader.py` due to its caching mechanism (which reloads if files change), meaning backend restarts are often not required for prompt updates to take effect.
-   **Deprecation of `prompts.json`**: Ensure that no new development relies on the old `prompts.json` file. All prompt logic should leverage the modular markdown system in the `prompts/` directory.