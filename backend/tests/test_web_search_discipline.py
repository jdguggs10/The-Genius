"""
Tests for Web Search Discipline Service (Step 4 Implementation)
"""

import pytest
from app.services.web_search_discipline import WebSearchDiscipline, SearchDecision

class TestWebSearchDiscipline:
    
    def setup_method(self):
        """Set up test instance."""
        self.discipline = WebSearchDiscipline(recency_threshold_days=7)
    
    def test_time_sensitive_keywords_trigger_search(self):
        """Test that time-sensitive keywords trigger mandatory search."""
        time_sensitive_queries = [
            "What's the latest injury news on Josh Allen?",
            "Should I start Davante Adams tonight?",
            "Current weather conditions for the game",
            "Recent performance trends for Christian McCaffrey",
            "Breaking news about the trade deadline",
            "Is Lamar Jackson questionable for this week?"
        ]
        
        for query in time_sensitive_queries:
            decision, reasoning = self.discipline.should_search(query)
            assert decision == SearchDecision.MANDATORY, f"Query should trigger search: {query}"
            assert "time-sensitive" in reasoning.lower(), f"Should cite time-sensitive reason: {reasoning}"
    
    def test_fantasy_context_triggers_search(self):
        """Test that fantasy sports context triggers search for active entities."""
        fantasy_queries = [
            "Should I start Derrick Henry or Alvin Kamara?",
            "Who should I pick up from waivers this week?",
            "Trade advice for my team",
            "Matchup analysis for Week 15",
            "DFS lineup recommendations",
            "Prop bet advice for Sunday games"
        ]
        
        for query in fantasy_queries:
            decision, reasoning = self.discipline.should_search(query)
            assert decision == SearchDecision.MANDATORY, f"Fantasy query should trigger search: {query}"
            assert ("active entities" in reasoning.lower() or "time-sensitive" in reasoning.lower()), f"Should cite active entities: {reasoning}"
    
    def test_historical_queries_skip_search(self):
        """Test that historical/theoretical queries skip search."""
        historical_queries = [
            "Who won the MVP in 2019?",
            "What are the general rules for PPR scoring?",
            "How does the playoff system work in fantasy football?",
            "Biography of Tom Brady",
            "History of the New England Patriots",
            "What if scenario: trading my entire team"
        ]
        
        for query in historical_queries:
            decision, reasoning = self.discipline.should_search(query)
            assert decision == SearchDecision.SKIP, f"Historical query should skip search: {query}"
            assert "historical" in reasoning.lower() or "theoretical" in reasoning.lower(), f"Should cite historical reason: {reasoning}"
    
    def test_user_override_bypass(self):
        """Test that user override commands bypass automatic decisions."""
        bypass_commands = ["/nosrch", "/nosearch", "--no-web-search"]
        
        # Test with a query that would normally trigger search
        base_query = "Latest injury report for Josh Allen"
        
        for command in bypass_commands:
            # Test as separate override parameter
            decision, reasoning = self.discipline.should_search(base_query, user_override=command)
            assert decision == SearchDecision.BYPASS, f"Override {command} should bypass search"
            assert "explicitly disabled" in reasoning.lower(), f"Should cite explicit disable: {reasoning}"
            
            # Test as part of query
            query_with_command = f"{base_query} {command}"
            decision, reasoning = self.discipline.should_search(query_with_command)
            assert decision == SearchDecision.BYPASS, f"Query with {command} should bypass search"
    
    def test_player_name_detection(self):
        """Test detection of player names as active entities."""
        player_queries = [
            "Should I start Josh Allen this week?",
            "How is Christian McCaffrey performing lately?",
            "Travis Kelce vs Mark Andrews matchup",
            "Thoughts on DeAndre Hopkins Jr. trade value?"
        ]
        
        for query in player_queries:
            has_active = self.discipline._has_recently_active_entities(query)
            assert has_active, f"Should detect player names as active entities: {query}"
    
    def test_date_pattern_detection(self):
        """Test detection of date patterns as time-sensitive."""
        date_queries = [
            "Weather forecast for 2024-01-15",
            "Week 15 rankings",
            "This Sunday's game predictions",
            "Next week's waiver targets",
            "Games on 12/25"
        ]
        
        for query in date_queries:
            is_time_sensitive = self.discipline._is_time_sensitive_query(query)
            assert is_time_sensitive, f"Should detect date patterns as time-sensitive: {query}"
    
    def test_query_classification(self):
        """Test query classification functionality."""
        test_cases = [
            ("Is Josh Allen injured?", "injury_status"),
            ("Should I start Derrick Henry?", "lineup_decision"),
            ("Who should I pick up from waivers?", "roster_management"),
            ("What's the weather for tonight's game?", "game_conditions"),
            ("Mahomes vs Allen matchup", "matchup_analysis"),
            ("Trade advice for my team", "trade_analysis"),
            ("General fantasy football question", "general_advice")
        ]
        
        for query, expected_classification in test_cases:
            classification = self.discipline._classify_query(query)
            assert classification == expected_classification, f"Query '{query}' should be classified as '{expected_classification}', got '{classification}'"
    
    def test_search_policy_payload_generation(self):
        """Test generation of search policy payload for API requests."""
        query = "Should I start Josh Allen tonight?"
        payload = self.discipline.get_search_policy_payload(query)
        
        # Check required fields
        assert "tool" in payload
        assert "policy" in payload
        assert "reasoning" in payload
        assert "inputs" in payload
        assert "metadata" in payload
        
        # Check values
        assert payload["tool"] == "web_search"
        assert payload["policy"] == "mandatory"
        assert payload["inputs"]["recency_days"] == 7
        assert "timestamp" in payload["metadata"]
        assert "query_length" in payload["metadata"]
    
    def test_conversation_context_integration(self):
        """Test that conversation context is properly considered."""
        conversation = [
            {"role": "user", "content": "Who are the top RBs this week?"},
            {"role": "assistant", "content": "Here are the top RBs..."},
            {"role": "user", "content": "What about injury concerns?"}
        ]
        
        decision, reasoning = self.discipline.should_search(
            "What about injury concerns?", 
            conversation_context=conversation
        )
        
        # Should trigger search due to injury keyword
        assert decision == SearchDecision.MANDATORY
        assert "time-sensitive" in reasoning.lower()
    
    def test_recency_threshold_configuration(self):
        """Test that recency threshold can be configured."""
        custom_discipline = WebSearchDiscipline(recency_threshold_days=14)
        assert custom_discipline.recency_threshold_days == 14
        
        payload = custom_discipline.get_search_policy_payload("Test query")
        assert payload["inputs"]["recency_days"] == 14
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty query
        decision, reasoning = self.discipline.should_search("")
        assert decision == SearchDecision.SKIP
        
        # None query (should handle gracefully)
        try:
            decision, reasoning = self.discipline.should_search(None)
            # Should handle None gracefully or raise appropriate error
        except (TypeError, AttributeError):
            # This is acceptable - None query is invalid input
            pass
        
        # Very long query
        long_query = "Should I start " + "Josh Allen " * 100 + "this week?"
        decision, reasoning = self.discipline.should_search(long_query)
        assert decision == SearchDecision.MANDATORY  # Should still detect fantasy context
    
    def test_keyword_variations(self):
        """Test that keyword variations are properly detected."""
        injury_variations = [
            "Is player hurt?",
            "injury report",
            "questionable status", 
            "ruled out",
            "game time decision",
            "gtd"
        ]
        
        for variation in injury_variations:
            is_time_sensitive = self.discipline._is_time_sensitive_query(variation)
            assert is_time_sensitive, f"Should detect injury variation: {variation}"

if __name__ == "__main__":
    pytest.main([__file__]) 