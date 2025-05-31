#!/usr/bin/env python3
"""
CLI Tool for Testing Web Search Discipline (Step 4 Implementation)

Usage:
    python test_search_discipline_cli.py
    python test_search_discipline_cli.py --query "Should I start Josh Allen tonight?"
    python test_search_discipline_cli.py --interactive
"""

import argparse
import json
import sys
from app.services.web_search_discipline import WebSearchDiscipline, SearchDecision

def test_example_queries():
    """Test a variety of example queries to demonstrate the search discipline logic."""
    discipline = WebSearchDiscipline()
    
    test_cases = [
        # Time-sensitive queries (should search)
        ("Latest injury report for Josh Allen", None, "Time-sensitive: injury keyword"),
        ("Should I start Davante Adams tonight?", None, "Time-sensitive: tonight"),
        ("Weather forecast for Sunday's game", None, "Time-sensitive: weather"),
        ("Breaking news about trade deadline", None, "Time-sensitive: breaking news"),
        
        # Fantasy context queries (should search) 
        ("Who should I pick up from waivers?", None, "Active entities: fantasy decisions"),
        ("Derrick Henry vs Alvin Kamara matchup", None, "Active entities: player analysis"),
        ("DFS lineup advice for this week", None, "Active entities: lineup decisions"),
        ("Trade value for Christian McCaffrey", None, "Active entities: trade analysis"),
        
        # Historical queries (should skip)
        ("Who won MVP in 2019?", None, "Historical: past season stats"),
        ("Tom Brady career statistics", None, "Historical: career overview"),
        ("How does PPR scoring work?", None, "Theoretical: rules explanation"),
        ("What if I drafted differently?", None, "Theoretical: hypothetical scenario"),
        
        # User override queries (should bypass)
        ("Latest injury report for Josh Allen", "/nosrch", "User override: bypass command"),
        ("Should I start Davante Adams tonight? /nosearch", None, "User override: in query"),
        ("Breaking news --no-web-search", None, "User override: flag format"),
    ]
    
    print("🔍 Web Search Discipline Test Results (Step 4 Implementation)")
    print("=" * 80)
    print()
    
    for i, (query, override, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print(f"Query: \"{query}\"")
        if override:
            print(f"Override: {override}")
        
        decision, reasoning = discipline.should_search(query, user_override=override)
        
        # Color coding for terminal output
        if decision == SearchDecision.MANDATORY:
            result_color = "\033[92m"  # Green
            result_text = "🔍 SEARCH"
        elif decision == SearchDecision.BYPASS:
            result_color = "\033[93m"  # Yellow
            result_text = "⚠️  BYPASS"
        else:
            result_color = "\033[91m"  # Red
            result_text = "⏭️  SKIP"
        
        reset_color = "\033[0m"
        
        print(f"Decision: {result_color}{result_text}{reset_color}")
        print(f"Reasoning: {reasoning}")
        
        # Show query analysis
        analysis = {
            "time_sensitive": discipline._is_time_sensitive_query(query),
            "active_entities": discipline._has_recently_active_entities(query),
            "classification": discipline._classify_query(query)
        }
        print(f"Analysis: {analysis}")
        print("-" * 80)
        print()

def interactive_mode():
    """Interactive mode for testing custom queries."""
    discipline = WebSearchDiscipline()
    
    print("🔍 Interactive Web Search Discipline Tester")
    print("Enter queries to test search decisions. Type 'quit' to exit.")
    print("Add '/nosrch' or similar commands to test overrides.")
    print("=" * 60)
    print()
    
    while True:
        try:
            query = input("Enter query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
                
            if not query:
                continue
            
            # Check for override commands in the query
            override = None
            for bypass_cmd in discipline.bypass_keywords:
                if bypass_cmd in query.lower():
                    override = bypass_cmd
                    break
            
            decision, reasoning = discipline.should_search(query, user_override=override)
            
            # Get full analysis
            payload = discipline.get_search_policy_payload(query, user_override=override)
            
            print()
            print(f"Decision: {decision.value.upper()}")
            print(f"Reasoning: {reasoning}")
            print(f"Classification: {payload['inputs']['query_classification']}")
            print(f"Time-sensitive: {discipline._is_time_sensitive_query(query)}")
            print(f"Active entities: {discipline._has_recently_active_entities(query)}")
            print()
            print("Full payload:")
            print(json.dumps(payload, indent=2, default=str))
            print("-" * 60)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()

def test_single_query(query: str, override: str = None):
    """Test a single query and show detailed results."""
    discipline = WebSearchDiscipline()
    
    print(f"🔍 Testing Query: \"{query}\"")
    if override:
        print(f"Override: {override}")
    print("=" * 60)
    
    decision, reasoning = discipline.should_search(query, user_override=override)
    payload = discipline.get_search_policy_payload(query, user_override=override)
    
    print(f"Decision: {decision.value.upper()}")
    print(f"Reasoning: {reasoning}")
    print()
    print("Detailed Analysis:")
    print(f"  Time-sensitive: {discipline._is_time_sensitive_query(query)}")
    print(f"  Active entities: {discipline._has_recently_active_entities(query)}")
    print(f"  Classification: {discipline._classify_query(query)}")
    print(f"  Time-sensitive keywords: {discipline._get_time_sensitive_reasons(query)}")
    print(f"  Active entity reasons: {discipline._get_active_entity_reasons(query)}")
    print()
    print("Full Policy Payload:")
    print(json.dumps(payload, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description="Test Web Search Discipline Logic")
    parser.add_argument("--query", "-q", help="Test a specific query")
    parser.add_argument("--override", "-o", help="Test with override command")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--examples", "-e", action="store_true", default=True, help="Run example test cases")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.query:
        test_single_query(args.query, args.override)
    else:
        test_example_queries()

if __name__ == "__main__":
    main() 