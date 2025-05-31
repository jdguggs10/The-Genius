"""
Snapshot Unit Tests for Prompt System
Tests that critical prompt content and structure remain intact.
"""

import pytest
from pathlib import Path
from app.services.prompt_loader import prompt_loader


class TestPromptSnapshots:
    """Test that prompt files contain required sections and headers."""
    
    def test_base_instructions_contains_policy_header(self):
        """Ensure base instructions always contain core policy section."""
        base_instructions = prompt_loader._load_universal_prompts()['base_instructions']
        assert "## Core Policy (Immutable)" in base_instructions
        assert "structured JSON format" in base_instructions
        
    def test_confidence_guidelines_contains_scoring_criteria(self):
        """Ensure confidence guidelines always contain scoring criteria."""
        confidence_guidelines = prompt_loader._load_universal_prompts()['confidence_guidelines']
        assert "## Scoring Criteria" in confidence_guidelines
        assert "0.9 - 1.0 (Very High Confidence)" in confidence_guidelines
        assert "0.1 - 0.2 (Very Low Confidence)" in confidence_guidelines
        
    def test_response_format_contains_json_structure(self):
        """Ensure response format always contains JSON structure requirements."""
        response_format = prompt_loader._load_universal_prompts()['response_format']
        assert "## JSON Structure Requirements" in response_format
        assert "main_advice (Required)" in response_format
        assert "confidence_score (Required)" in response_format
        
    def test_web_search_guidelines_contains_priority_sources(self):
        """Ensure web search guidelines always contain priority information sources."""
        web_search = prompt_loader._load_universal_prompts()['web_search_guidelines']
        assert "## Priority Information Sources" in web_search
        assert "Official team websites" in web_search
        
    def test_workflow_instructions_contains_steps(self):
        """Ensure workflow instructions contain context-aware analysis steps."""
        workflow = prompt_loader._load_universal_prompts()['workflow_instructions']
        assert "## Context-Aware Analysis Guidelines" in workflow
        assert "Conversation Context Assessment" in workflow
        assert "Web Search Strategy" in workflow
        
    def test_all_prompt_files_have_version_headers(self):
        """Ensure all prompt files have proper version headers."""
        prompts_path = Path(__file__).parent.parent.parent / "shared-resources" / "prompts"
        
        # Check universal prompts
        universal_files = [
            "base-instructions@1.1.0.md",
            "workflow-instructions@1.0.0.md", 
            "confidence-guidelines@1.0.0.md",
            "response-format@1.0.0.md",
            "web-search-guidelines@1.0.0.md"
        ]
        
        for filename in universal_files:
            file_path = prompts_path / "universal" / filename
            if file_path.exists():
                content = file_path.read_text()
                assert content.startswith("# "), f"{filename} should start with a header"
                assert " v" in content.split('\n')[0], f"{filename} should have version in header"
        
        # Check sport-specific prompts
        sport_dirs = ["football", "baseball", "basketball"]
        for sport in sport_dirs:
            sport_file = prompts_path / sport / "system-prompt@1.0.0.md"
            if sport_file.exists():
                content = sport_file.read_text()
                assert content.startswith("# "), f"{sport} prompt should start with header"
                assert " v1.0.0" in content.split('\n')[0], f"{sport} prompt should have v1.0.0 in header"
                
    def test_prompt_loader_can_load_all_types(self):
        """Ensure prompt loader can successfully load all prompt types."""
        # Test universal prompts
        default_prompt = prompt_loader.get_system_prompt("default")
        assert len(default_prompt) > 100, "Default prompt should have substantial content"
        
        detailed_prompt = prompt_loader.get_system_prompt("detailed")
        assert len(detailed_prompt) > 100, "Detailed prompt should have substantial content"
        
        # Test sport-specific prompts
        for sport in ["football", "baseball", "basketball"]:
            sport_prompt = prompt_loader.get_system_prompt(sport)
            assert len(sport_prompt) > 100, f"{sport} prompt should have substantial content"
            assert sport.title() in sport_prompt, f"{sport} prompt should mention {sport}"
            
    def test_prompt_files_exist_with_correct_naming(self):
        """Ensure all expected prompt files exist with semantic versioning."""
        prompts_path = Path(__file__).parent.parent.parent / "shared-resources" / "prompts"
        
        # Universal files
        expected_universal = [
            "base-instructions@1.1.0.md",
            "workflow-instructions@1.0.0.md",
            "confidence-guidelines@1.0.0.md", 
            "response-format@1.0.0.md",
            "web-search-guidelines@1.0.0.md"
        ]
        
        for filename in expected_universal:
            file_path = prompts_path / "universal" / filename
            assert file_path.exists(), f"Universal prompt file {filename} should exist"
            
        # Sport-specific files
        for sport in ["football", "baseball", "basketball"]:
            sport_file = prompts_path / sport / "system-prompt@1.0.0.md"
            assert sport_file.exists(), f"Sport prompt file for {sport} should exist"
            
    def test_no_unversioned_prompt_files_remain(self):
        """Ensure no old unversioned prompt files remain."""
        prompts_path = Path(__file__).parent.parent.parent / "shared-resources" / "prompts"
        
        # Check that no .md files exist without @version format (except README.md)
        for md_file in prompts_path.rglob("*.md"):
            if md_file.name == "README.md":
                continue
            assert "@" in md_file.name, f"Prompt file {md_file} should have semantic versioning (@x.y.z)"
            assert md_file.name.count("@") == 1, f"Prompt file {md_file} should have exactly one @ symbol" 