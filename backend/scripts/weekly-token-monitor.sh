#!/bin/bash

# Weekly Token Monitor - Step 8 Implementation
# Automated token usage tracking and optimization alerts

set -e

echo "🔍 Weekly Token Monitoring - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"

# Change to backend directory
cd "$(dirname "$0")/.."

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run token tracking
echo "📊 Analyzing current token usage..."
npm run token-track

# Generate full report
echo "📋 Generating detailed analysis..."
npm run token-analysis > "logs/token-analysis-$(date '+%Y-%m-%d').log" 2>&1

# Check for significant changes
echo "📈 Checking for usage trends..."

LOG_FILE="scripts/token-usage-log.json"
if [ -f "$LOG_FILE" ]; then
    # Get the last two entries to compare
    CURRENT_TOKENS=$(jq '.[length-1].totalTokens' "$LOG_FILE")
    PREVIOUS_TOKENS=$(jq '.[length-2].totalTokens' "$LOG_FILE" 2>/dev/null || echo "0")
    
    if [ "$PREVIOUS_TOKENS" != "0" ] && [ "$PREVIOUS_TOKENS" != "null" ]; then
        CHANGE=$((CURRENT_TOKENS - PREVIOUS_TOKENS))
        PERCENT_CHANGE=$(echo "scale=2; $CHANGE * 100 / $PREVIOUS_TOKENS" | bc -l 2>/dev/null || echo "0")
        
        echo "Token change since last week: $CHANGE tokens ($PERCENT_CHANGE%)"
        
        # Alert if significant increase (>10%)
        if (( $(echo "$PERCENT_CHANGE > 10" | bc -l) )); then
            echo "⚠️  ALERT: Significant token increase detected!"
            echo "   Previous: $PREVIOUS_TOKENS tokens"
            echo "   Current:  $CURRENT_TOKENS tokens"
            echo "   Change:   +$CHANGE tokens (+$PERCENT_CHANGE%)"
            
            # Could send email or Slack notification here
            # slack-notify "Token usage increased by $PERCENT_CHANGE% this week"
        elif (( $(echo "$PERCENT_CHANGE < -10" | bc -l) )); then
            echo "✅ Excellent: Token usage decreased by $PERCENT_CHANGE% this week!"
        fi
    fi
fi

# Check for high-usage files
echo "🎯 Checking for optimization opportunities..."
HIGH_TOKEN_COUNT=$(jq '.[length-1].topFiles | length' "$LOG_FILE")
if [ "$HIGH_TOKEN_COUNT" -gt 0 ]; then
    echo "Top token consumers:"
    jq -r '.[length-1].topFiles[] | "  • \(.file): \(.tokens) tokens"' "$LOG_FILE"
fi

# Archive old logs (keep last 12 weeks)
echo "🗂️  Archiving old logs..."
if [ -d "logs" ]; then
    find logs/ -name "token-analysis-*.log" -mtime +84 -delete
fi

echo "✅ Weekly token monitoring complete!"
echo "================================================================" 