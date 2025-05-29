"""
Modular Prompt Loading System
Combines universal base prompts with sport-specific prompts for systematic prompt management.
"""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptLoader:
    """Loads and combines prompts from the modular prompt system"""
    
    def __init__(self, prompts_base_path: Optional[str] = None):
        if prompts_base_path is None:
            # Default to shared-resources/prompts from the project root
            current_dir = Path(__file__).parent
            self.prompts_path = current_dir / ".." / ".." / ".." / "shared-resources" / "prompts"
        else:
            self.prompts_path = Path(prompts_base_path)
        
        self.universal_path = self.prompts_path / "universal"
        
        # Cache for loaded prompts to avoid repeated file I/O
        self._prompt_cache: Dict[str, str] = {}
    
    def _load_file_content(self, file_path: Path) -> str:
        """Load content from a markdown file with caching"""
        cache_key = str(file_path)
        
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self._prompt_cache[cache_key] = content
                return content
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error loading prompt file {file_path}: {e}")
            return ""
    
    def _load_universal_prompts(self) -> Dict[str, str]:
        """Load all universal prompt components"""
        universal_files = {
            'base_instructions': 'base-instructions.md',
            'confidence_guidelines': 'confidence-guidelines.md', 
            'response_format': 'response-format.md',
            'web_search_guidelines': 'web-search-guidelines.md'
        }
        
        universal_prompts = {}
        for key, filename in universal_files.items():
            file_path = self.universal_path / filename
            universal_prompts[key] = self._load_file_content(file_path)
        
        return universal_prompts
    
    def _load_sport_specific_prompt(self, sport: str) -> str:
        """Load sport-specific system prompt"""
        sport_path = self.prompts_path / sport / "system-prompt.md"
        return self._load_file_content(sport_path)
    
    def get_system_prompt(self, prompt_type: str = "default") -> str:
        """
        Build complete system prompt by combining universal base + sport-specific content
        
        Args:
            prompt_type: Type of prompt ("default", "detailed", "baseball", "football", "basketball")
        
        Returns:
            Complete system prompt string
        """
        # Check for environment override first
        env_prompt = os.getenv("SYSTEM_PROMPT")
        if env_prompt:
            logger.info("Using system prompt from environment variable")
            return env_prompt
        
        # Load universal components
        universal = self._load_universal_prompts()
        
        # Combine universal base instructions with sport-specific content
        if prompt_type in ["baseball", "football", "basketball"]:
            sport_specific = self._load_sport_specific_prompt(prompt_type)
            
            # Combine base instructions with sport-specific prompt
            if sport_specific:
                combined_prompt = f"{universal['base_instructions']}\n\n{sport_specific}"
            else:
                logger.warning(f"Sport-specific prompt not found for {prompt_type}, using base instructions only")
                combined_prompt = universal['base_instructions']
        else:
            # For "default" or "detailed", use enhanced base instructions
            if prompt_type == "detailed":
                enhanced_base = universal['base_instructions'].replace(
                    "Your primary goal is to provide actionable, data-driven advice",
                    "Your primary goal is to provide comprehensive, data-driven analysis with detailed reasoning and confidence assessments"
                )
                combined_prompt = enhanced_base
            else:
                combined_prompt = universal['base_instructions']
        
        # Fallback if no content was loaded
        if not combined_prompt.strip():
            logger.warning("No prompt content loaded, using hardcoded fallback")
            return "You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy."
        
        return combined_prompt
    
    def build_full_prompt(self, user_prompt: str, system_prompt: str, schema: dict, enable_web_search: bool = False) -> str:
        """
        Build the complete prompt with system instructions, universal guidelines, and user input
        
        Args:
            user_prompt: The user's question/request
            system_prompt: Base system prompt for the AI
            schema: JSON schema for structured responses
            enable_web_search: Whether web search is enabled
        
        Returns:
            Complete formatted prompt
        """
        universal = self._load_universal_prompts()
        
        # Build instruction components
        components = [system_prompt]
        
        # Add response format guidelines
        if universal['response_format']:
            components.append(universal['response_format'])
        
        # Add confidence guidelines
        if universal['confidence_guidelines']:
            components.append(universal['confidence_guidelines'])
        
        # Add web search guidelines if enabled
        if enable_web_search and universal['web_search_guidelines']:
            components.append(universal['web_search_guidelines'])
        
        # Add schema requirement
        schema_instruction = f"Please respond with structured JSON that matches this exact schema: {schema}"
        components.append(schema_instruction)
        
        # Combine all components
        full_instructions = "\n\n".join(components)
        
        # Add user prompt
        return f"{full_instructions}\n\nUser: {user_prompt}"
    
    def clear_cache(self):
        """Clear the prompt cache (useful for development/testing)"""
        self._prompt_cache.clear()
        logger.info("Prompt cache cleared")
    
    def get_available_prompt_types(self) -> List[str]:
        """Get list of available prompt types"""
        base_types = ["default", "detailed"]
        
        # Check for sport-specific directories
        sport_types = []
        try:
            for item in self.prompts_path.iterdir():
                if item.is_dir() and item.name != "universal":
                    sport_types.append(item.name)
        except Exception as e:
            logger.error(f"Error scanning prompt directories: {e}")
        
        return base_types + sport_types

# Global instance for easy access
prompt_loader = PromptLoader() 