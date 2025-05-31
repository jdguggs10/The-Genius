"""
Web Search Discipline Service

Implements step 4 of the prompt improvement guide:
Systematic rule-based web search decisions instead of LLM token-consuming decisions.

Rules:
- IF (query_is_time_sensitive OR entity_recently_active ≤ 7 days) THEN search()
- ELSE skip_search()
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class SearchDecision(Enum):
    MANDATORY = "mandatory"
    SKIP = "skip"
    BYPASS = "bypass"  # User override

class WebSearchDiscipline:
    """
    Systematic web search decision engine that removes the burden of 
    search decisions from the LLM, saving tokens and improving consistency.
    """
    
    def __init__(self, recency_threshold_days: int = 7):
        self.recency_threshold_days = recency_threshold_days
        
        # Time-sensitive keywords that always trigger search
        self.time_sensitive_keywords = {
            # Immediate status
            "today", "tonight", "now", "current", "latest", "recent", "breaking",
            "this week", "this weekend", "upcoming", "tomorrow",
            
            # Injury and availability
            "injury", "injured", "hurt", "questionable", "doubtful", "out", 
            "gtd", "game time decision", "dnp", "limited", "full practice",
            "active", "inactive", "ruled out", "cleared",
            
            # Performance trends  
            "trending", "hot", "cold", "slump", "streak", "surge", "momentum",
            "last game", "last week", "past few", "since",
            
            # Weather and conditions
            "weather", "wind", "rain", "snow", "temperature", "dome", "outdoor",
            
            # Lineup and usage
            "starting", "bench", "snap count", "targets", "carries", "usage",
            "role change", "promoted", "demoted", "depth chart",
            
            # News and updates
            "news", "update", "report", "announced", "confirmed", "suspended",
            "trade", "waiver", "pickup", "drop", "add"
        }
        
        # Entity types that are frequently active/changing
        self.active_entity_types = {
            # Player-related entities that change frequently
            "player_performance", "player_status", "player_news",
            
            # Team-related entities  
            "team_news", "coaching_changes", "lineup_changes",
            
            # Game-related entities
            "matchup", "game_conditions", "betting_lines",
            
            # Fantasy-related entities
            "waiver_wire", "trade_targets", "rankings"
        }
        
        # Bypass keywords that user can use to skip search
        self.bypass_keywords = {
            "/nosrch", "/nosearch", "/skip-search", "--no-web-search"
        }
        
    def should_search(self, user_query: str, conversation_context: Optional[List[Dict]] = None, 
                     user_override: Optional[str] = None) -> Tuple[SearchDecision, str]:
        """
        Determine if web search should be performed based on systematic rules.
        
        Args:
            user_query: The user's query text
            conversation_context: Previous conversation messages for context
            user_override: Explicit user override command
            
        Returns:
            Tuple of (SearchDecision, reasoning)
        """
        
        # Check for user bypass commands first
        if user_override or any(bypass in user_query.lower() for bypass in self.bypass_keywords):
            return SearchDecision.BYPASS, "User explicitly disabled search"
        
        # Check for clearly historical/theoretical queries first
        if self._is_historical_query(user_query):
            return SearchDecision.SKIP, "Query appears historical/theoretical with no time-sensitive elements"
            
        # Apply the core rule: time_sensitive OR entity_recently_active
        is_time_sensitive = self._is_time_sensitive_query(user_query)
        has_active_entities = self._has_recently_active_entities(user_query, conversation_context)
        
        if is_time_sensitive:
            return SearchDecision.MANDATORY, f"Time-sensitive query detected: {self._get_time_sensitive_reasons(user_query)}"
            
        if has_active_entities:
            return SearchDecision.MANDATORY, f"Recently active entities detected: {self._get_active_entity_reasons(user_query)}"
            
        # Default to skip for other queries
        return SearchDecision.SKIP, "Query appears historical/theoretical with no time-sensitive elements"
        
    def _is_time_sensitive_query(self, query: str) -> bool:
        """Check if query contains time-sensitive keywords or patterns."""
        query_lower = query.lower()
        
        # Direct keyword matches
        if any(keyword in query_lower for keyword in self.time_sensitive_keywords):
            return True
            
        # Date pattern detection (YYYY-MM-DD, MM/DD, "this Sunday", etc.)
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # 2024-01-15
            r'\b\d{1,2}/\d{1,2}\b',    # 1/15, 01/15  
            r'\bthis (sunday|monday|tuesday|wednesday|thursday|friday|saturday)\b',
            r'\bnext (week|game|sunday|monday|tuesday|wednesday|thursday|friday|saturday)\b',
            r'\b(week \d+|wk \d+)\b'   # Week 15, Wk 15
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, query_lower):
                return True
                
        return False
        
    def _has_recently_active_entities(self, query: str, conversation_context: Optional[List[Dict]] = None) -> bool:
        """
        Check if query involves entities that are likely to have recent updates.
        In a full implementation, this could check against a database of entity activity.
        """
        query_lower = query.lower()
        
        # Fantasy sports queries are generally about active entities
        fantasy_indicators = [
            "start", "sit", "lineup", "roster", "waiver", "trade", "pickup", "drop",
            "matchup", "projection", "ranking", "advice", "play", "avoid",
            "dfs", "daily fantasy", "prop bet", "anytime td", "over/under",
            "performing", "lately", "trends", "value", "target"  # Added more indicators
        ]
        
        if any(indicator in query_lower for indicator in fantasy_indicators):
            return True
            
        # Player name detection (simplified - could be enhanced with NER)
        # Look for patterns like "Should I start [Name Name]?" or "[Name] vs [Team]"
        player_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Likely player names (Title Case)
            r'\b(start|sit|play|bench) [A-Z]',  # Action followed by name
            r'\b[A-Z][a-z]+( Jr\.?| Sr\.?| III)?\b vs\b'  # Name vs (matchup context)
        ]
        
        for pattern in player_patterns:
            if re.search(pattern, query):
                return True
        
        # Check for football positions that suggest active player discussion
        position_patterns = [
            r'\b(QB|RB|WR|TE|K|DST|DEF)\b',  # Position abbreviations
            r'\b(quarterback|running back|wide receiver|tight end|kicker|defense)\b'
        ]
        
        for pattern in position_patterns:
            if re.search(pattern, query_lower):
                return True
                
        return False
        
    def _get_time_sensitive_reasons(self, query: str) -> str:
        """Get specific time-sensitive keywords found in the query."""
        found_keywords = []
        query_lower = query.lower()
        
        for keyword in self.time_sensitive_keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)
                
        return ", ".join(found_keywords[:3])  # Limit to top 3 for brevity
        
    def _get_active_entity_reasons(self, query: str) -> str:
        """Get specific active entity indicators found in the query."""
        query_lower = query.lower()
        reasons = []
        
        if any(indicator in query_lower for indicator in ["start", "sit", "lineup", "roster"]):
            reasons.append("lineup decisions")
            
        if any(indicator in query_lower for indicator in ["waiver", "trade", "pickup", "drop"]):
            reasons.append("roster management") 
            
        if any(indicator in query_lower for indicator in ["matchup", "projection", "ranking"]):
            reasons.append("performance analysis")
            
        if any(indicator in query_lower for indicator in ["performing", "lately", "trends", "value"]):
            reasons.append("performance trends")
            
        return ", ".join(reasons) if reasons else "fantasy sports context"
        
    def get_search_policy_payload(self, user_query: str, conversation_context: Optional[List[Dict]] = None,
                                user_override: Optional[str] = None) -> Dict:
        """
        Generate search policy payload for API requests.
        
        Returns:
            Dictionary with search tool configuration
        """
        decision, reasoning = self.should_search(user_query, conversation_context, user_override)
        
        payload = {
            "tool": "web_search",
            "policy": decision.value,
            "reasoning": reasoning,
            "inputs": {
                "recency_days": self.recency_threshold_days,
                "query_classification": self._classify_query(user_query)
            }
        }
        
        # Add metadata for monitoring
        payload["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(user_query),
            "has_conversation_context": conversation_context is not None,
            "user_override_detected": decision == SearchDecision.BYPASS
        }
        
        return payload
        
    def _classify_query(self, query: str) -> str:
        """Classify the type of query for better search optimization."""
        query_lower = query.lower()
        
        # Order matters - check more specific patterns first
        if any(word in query_lower for word in ["injury", "injured", "hurt", "questionable", "out"]):
            return "injury_status"
        elif any(word in query_lower for word in ["start", "sit", "lineup"]):
            return "lineup_decision"  
        elif any(word in query_lower for word in ["waiver", "pickup", "add", "drop"]):
            return "roster_management"
        elif any(word in query_lower for word in ["weather", "wind", "rain", "conditions"]):
            return "game_conditions"
        elif any(word in query_lower for word in ["matchup", "vs", "against"]):
            return "matchup_analysis"
        elif any(word in query_lower for word in ["trade", "target", "value"]):
            return "trade_analysis"
        # Check for more specific historical/rules patterns
        elif any(phrase in query_lower for phrase in ["rules for", "how does the", "what are the general rules", "biography of", "history of", "won mvp", "playoff system work"]):
            return "historical_rules"
        else:
            return "general_advice"

    def _is_historical_query(self, query: str) -> bool:
        """Check if query is clearly historical or theoretical and should skip search."""
        query_lower = query.lower()
        
        # Strong indicators of historical/theoretical content
        historical_indicators = [
            "who won", "mvp in", "biography", "history of", "career statistics",
            "what are the general rules", "how does the playoff system work",
            "rules for", "what if scenario", "hypothetical", "in 2019", "in 2020",
            "last season", "career stats", "all time", "hall of fame"
        ]
        
        # Check for historical patterns
        for indicator in historical_indicators:
            if indicator in query_lower:
                return True
        
        # Year patterns for past data
        year_patterns = [
            r'\b(19|20)\d{2}\b',  # Years like 1998, 2019, etc.
            r'\blast (year|season)\b',
            r'\bcareer\b',
            r'\ball[- ]time\b'
        ]
        
        for pattern in year_patterns:
            if re.search(pattern, query_lower):
                return True
                
        return False

# Global instance for easy access
web_search_discipline = WebSearchDiscipline() 