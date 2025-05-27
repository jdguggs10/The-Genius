#!/usr/bin/env python3
"""
Test the frontend web search detection logic
"""

def test_web_search_detection(input_text):
    """Replicate the frontend web search detection logic"""
    
    # Handle explicit "search:" prefix
    if input_text.lower().startswith('search:'):
        return True, input_text[7:].strip()
    
    # Auto-detect if web search should be enabled based on keywords
    input_lower = input_text.lower()
    web_search_keywords = [
        'stats', 'current', 'latest', 'today', 'now', 'recent', 'this week',
        'who plays', 'schedule', 'game', 'match', 'upcoming', 'when',
        'injury report', 'news', 'update', 'status', 'live', 'real-time',
        'search', 'find', 'look up', 'check', 'what happened'
    ]
    
    # Also check for common search phrases
    search_phrases = [
        'search the internet',
        'search for',
        'look up',
        'find out',
        'check online',
        'browse the web',
        'get current',
        'get latest',
        'real time',
        'live data'
    ]
    
    enable_web_search = any(keyword in input_lower for keyword in web_search_keywords) or \
                       any(phrase in input_lower for phrase in search_phrases)
    
    return enable_web_search, input_text

def main():
    """Test various inputs"""
    test_cases = [
        "Who do the Yankees play today?",
        "Who do the Yankees play today? Search the internet if necessary",
        "Search for who the Yankees play today",
        "search: who do the Yankees play today",
        "Should I start Patrick Mahomes?",
        "Get me the latest stats for Christian McCaffrey",
        "What's the current injury report for the Giants?",
        "When is the next game?",
        "Tell me about fantasy football"
    ]
    
    print("Testing frontend web search detection logic:")
    print("=" * 60)
    
    for test_input in test_cases:
        enable_search, actual_input = test_web_search_detection(test_input)
        status = "✅ WEB SEARCH" if enable_search else "❌ NO SEARCH"
        print(f"{status}: '{test_input}'")
        if test_input != actual_input:
            print(f"    → Processed as: '{actual_input}'")
        print()

if __name__ == "__main__":
    main() 