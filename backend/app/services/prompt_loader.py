"""
Modular Prompt Loading System
Combines universal base prompts with sport-specific prompts for systematic prompt management.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptLoader:
    """Loads and combines prompts from the modular prompt system"""
    
    def __init__(self, prompts_base_path: Optional[str] = None):
        if prompts_base_path is None:
            # Check if we're in a Docker container (working dir is /code)
            # or in development (where we need to go up to project root)
            current_dir = Path(__file__).parent
            
            # Try Docker path first (./shared-resources from working directory)
            docker_path = Path.cwd() / "shared-resources" / "prompts"
            
            # Try development path (go up to project root)
            dev_path = current_dir / ".." / ".." / ".." / "shared-resources" / "prompts"
            
            # Debug logging
            logger.info(f"Current working directory: {Path.cwd()}")
            logger.info(f"Current file directory: {current_dir}")
            logger.info(f"Trying Docker path: {docker_path} (exists: {docker_path.exists()})")
            logger.info(f"Trying dev path: {dev_path} (exists: {dev_path.exists()})")
            
            if docker_path.exists():
                self.prompts_path = docker_path
                logger.info(f"Using Docker prompts path: {docker_path}")
            elif dev_path.exists():
                self.prompts_path = dev_path
                logger.info(f"Using development prompts path: {dev_path}")
            else:
                # Fallback to Docker path and let it fail later with better error messages
                self.prompts_path = docker_path
                logger.warning(f"Neither Docker path {docker_path} nor dev path {dev_path} exists, using Docker path as fallback")
                # Additional debug: list contents of current working directory
                try:
                    logger.warning(f"Contents of {Path.cwd()}: {list(Path.cwd().iterdir())}")
                except Exception as e:
                    logger.error(f"Could not list contents of {Path.cwd()}: {e}")
        else:
            self.prompts_path = Path(prompts_base_path)
        
        self.universal_path = self.prompts_path / "universal"
        logger.info(f"Final prompts_path: {self.prompts_path}")
        logger.info(f"Universal path: {self.universal_path} (exists: {self.universal_path.exists()})")
        
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
            'base_instructions': 'base-instructions@1.2.0.md',
            'legacy_base_instructions': 'base-instructions@1.1.0.md',  # Fallback for non-Step 2
            'response_format': 'response-format@1.0.0.md',
            'confidence_guidelines': 'confidence-guidelines@1.0.0.md',
            'assistant_workflow': 'assistant-workflow@1.0.0.md',
            'runtime_workflow': 'runtime-workflow@1.0.0.md',
            'web_search_guidelines': 'web-search-guidelines@1.2.0.md'  # Updated to latest version
        }
        
        universal_prompts = {}
        for key, filename in universal_files.items():
            file_path = self.universal_path / filename
            universal_prompts[key] = self._load_file_content(file_path)
        
        return universal_prompts
    
    def _load_sport_specific_prompt(self, sport: str) -> str:
        """Load sport-specific system prompt"""
        sport_path = self.prompts_path / sport / "system-prompt@1.0.0.md"
        return self._load_file_content(sport_path)
    
    def get_system_prompt(self, prompt_type: str = "default", use_slim_prompt: bool = True) -> str:
        """
        Build complete system prompt by combining universal base + sport-specific content
        
        Args:
            prompt_type: Type of prompt ("default", "detailed", "baseball", "football", "basketball")
            use_slim_prompt: Whether to use the new slim system prompt (Step 2 implementation)
        
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
        
        # Step 2: Use slim base instructions by default
        base_key = 'base_instructions' if use_slim_prompt else 'legacy_base_instructions'
        base_instructions = universal.get(base_key, universal.get('legacy_base_instructions', ''))
        
        # Combine universal base instructions with sport-specific content
        if prompt_type in ["baseball", "football", "basketball"]:
            sport_specific = self._load_sport_specific_prompt(prompt_type)
            
            # Combine base instructions with sport-specific prompt
            if sport_specific:
                combined_prompt = f"{base_instructions}\n\n{sport_specific}"
            else:
                logger.warning(f"Sport-specific prompt not found for {prompt_type}, using base instructions only")
                combined_prompt = base_instructions
        else:
            # For "default" or "detailed", use base instructions
            combined_prompt = base_instructions
        
        # Fallback if no content was loaded
        if not combined_prompt.strip():
            logger.warning("No prompt content loaded, using hardcoded fallback")
            return "You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy."
        
        return combined_prompt
    
    def get_assistant_workflow_template(self, current_date: str = None) -> str:
        """
        Get the assistant workflow template for injection into conversation
        
        Args:
            current_date: Current date string to inject into template
            
        Returns:
            Assistant workflow template with date populated
        """
        universal = self._load_universal_prompts()
        runtime_workflow = universal.get('runtime_workflow', '')
        
        if current_date is None:
            current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Replace placeholder with actual date
        return runtime_workflow.replace("{current_date}", current_date)
    
    def build_conversation_messages(self, user_prompt: str, system_prompt: str, schema: dict, 
                                  enable_web_search: bool = False, use_slim_prompt: bool = True) -> List[Dict[str, str]]:
        """
        Build conversation messages for Responses API with Step 2 implementation
        
        Args:
            user_prompt: The user's question/request
            system_prompt: Base system prompt for the AI
            schema: JSON schema for structured responses
            enable_web_search: Whether web search is enabled
            use_slim_prompt: Whether to use Step 2 slim prompt architecture
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = []
        
        if use_slim_prompt:
            # Step 2: Separate system prompt and assistant workflow
            universal = self._load_universal_prompts()
            
            # System message: Only immutable policy
            system_content = system_prompt
            
            # Add response format to system prompt
            if universal['response_format']:
                system_content += f"\n\n{universal['response_format']}"
                
            # Add confidence guidelines to system prompt
            if universal['confidence_guidelines']:
                system_content += f"\n\n{universal['confidence_guidelines']}"
            
            # Add schema requirement to system prompt with emphasis on required fields
            schema_instruction = f"\n\nIMPORTANT: Please respond with structured JSON that matches this exact schema: {schema}\nThe 'main_advice' field is STRICTLY REQUIRED - all responses MUST include this field or they will fail validation. Always ensure your response includes the 'main_advice' field with a clear, actionable recommendation."
            system_content += schema_instruction
            
            messages.append({"role": "system", "content": system_content})
            
            # Assistant message: Runtime workflow instructions
            workflow_template = self.get_assistant_workflow_template()
            if workflow_template:
                messages.append({"role": "assistant", "content": workflow_template})
            
            # Add web search guidelines as assistant message if enabled
            if enable_web_search and universal['web_search_guidelines']:
                web_search_guidance = f"## Web Search Guidelines\n{universal['web_search_guidelines']}"
                messages.append({"role": "assistant", "content": web_search_guidance})
            
        else:
            # Legacy: Single system message with everything
            messages = [{"role": "system", "content": self.build_full_prompt(user_prompt, system_prompt, schema, enable_web_search)}]
            return messages
        
        # User message
        messages.append({"role": "user", "content": user_prompt})
        
        return messages

    def build_full_prompt(self, user_prompt: str, system_prompt: str, schema: dict, enable_web_search: bool = False) -> str:
        """
        Build the complete prompt with system instructions, universal guidelines, and user input
        Legacy method for backward compatibility
        
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
        
        # Add schema requirement with emphasis on required fields
        schema_instruction = f"IMPORTANT: Please respond with structured JSON that matches this exact schema: {schema}\nThe 'main_advice' field is STRICTLY REQUIRED - all responses MUST include this field or they will fail validation. Always ensure your response includes the 'main_advice' field with a clear, actionable recommendation."
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