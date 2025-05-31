#!/usr/bin/env node

/**
 * Token Estimator - Step 8 Implementation
 * Tracks token usage across prompts and estimates costs
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Rough GPT-4 token estimation (more precise with tiktoken library)
function estimateTokens(text) {
  // Rough estimation: ~4 characters per token for English text
  // This is a simplified estimate - use tiktoken for production
  return Math.ceil(text.length / 4);
}

function analyzePromptFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const tokens = estimateTokens(content);
  const lines = content.split('\n').length;
  
  return {
    file: path.relative(process.cwd(), filePath),
    tokens,
    lines,
    characters: content.length,
    avgTokensPerLine: Math.round(tokens / lines)
  };
}

function findOptimizationOpportunities(content, filePath) {
  const opportunities = [];
  
  // Check for ALL-CAPS sections
  const allCapsMatches = content.match(/[A-Z]{5,}/g);
  if (allCapsMatches && allCapsMatches.length > 3) {
    opportunities.push({
      type: 'ALL_CAPS',
      count: allCapsMatches.length,
      suggestion: 'Replace with ### markdown headings'
    });
  }
  
  // Check for long lists that could be replaced with IDs
  const listItems = content.match(/^[\s]*[-*+]\s+.+$/gm);
  if (listItems && listItems.length > 10) {
    opportunities.push({
      type: 'LONG_ENUMERATION',
      count: listItems.length,
      suggestion: `Replace with reference ID like 'MetricSet: ${path.basename(filePath, '.md')}_v1'`
    });
  }
  
  // Check for repeated static data
  const staticDataKeywords = ['factors', 'dimensions', 'stats', 'metrics', 'rankings'];
  const staticDataCount = staticDataKeywords.reduce((count, keyword) => {
    const matches = content.toLowerCase().match(new RegExp(keyword, 'g'));
    return count + (matches ? matches.length : 0);
  }, 0);
  
  if (staticDataCount > 15) {
    opportunities.push({
      type: 'STATIC_DATA',
      count: staticDataCount,
      suggestion: 'Consider moving to vector DB with reference IDs'
    });
  }
  
  return opportunities;
}

function generateReport() {
  console.log('🔍 Token Usage Analysis Report');
  console.log('================================\n');
  
  // Fix path - need to go up from backend directory
  const promptPattern = path.join('..', 'shared-resources', 'prompts', '**', '*.md');
  const promptFiles = glob.sync(promptPattern);
  
  console.log(`Found ${promptFiles.length} prompt files`);
  
  if (promptFiles.length === 0) {
    console.log('❌ No prompt files found. Check directory structure.');
    return;
  }
  
  const analyses = promptFiles.map(analyzePromptFile);
  
  // Sort by token count (highest first)
  analyses.sort((a, b) => b.tokens - a.tokens);
  
  console.log('📊 Token Usage by File:');
  console.log('------------------------');
  analyses.forEach(analysis => {
    console.log(`${analysis.file.padEnd(50)} ${analysis.tokens.toString().padStart(6)} tokens`);
  });
  
  const totalTokens = analyses.reduce((sum, a) => sum + a.tokens, 0);
  const avgTokensPerFile = Math.round(totalTokens / analyses.length);
  
  console.log(`\n📈 Summary Statistics:`);
  console.log(`Total tokens across all prompts: ${totalTokens}`);
  console.log(`Average tokens per file: ${avgTokensPerFile}`);
  
  if (analyses.length > 0) {
    console.log(`Largest file: ${analyses[0].file} (${analyses[0].tokens} tokens)`);
  }
  
  // Cost estimation (GPT-4 pricing as of 2024)
  const inputCostPer1kTokens = 0.03; // $0.03 per 1K input tokens
  const outputCostPer1kTokens = 0.06; // $0.06 per 1K output tokens
  
  // Estimate per-conversation cost (assume 2x tokens for output)
  const estimatedCostPerConversation = (totalTokens * inputCostPer1kTokens / 1000) + 
                                      (totalTokens * 2 * outputCostPer1kTokens / 1000);
  
  console.log(`\n💰 Cost Estimation:`);
  console.log(`Estimated cost per conversation: $${estimatedCostPerConversation.toFixed(4)}`);
  console.log(`Estimated cost per 1000 conversations: $${(estimatedCostPerConversation * 1000).toFixed(2)}`);
  
  // Optimization opportunities
  console.log(`\n🚀 Optimization Opportunities:`);
  console.log(`------------------------------`);
  
  promptFiles.forEach(filePath => {
    const content = fs.readFileSync(filePath, 'utf8');
    const opportunities = findOptimizationOpportunities(content, filePath);
    
    if (opportunities.length > 0) {
      console.log(`\n${path.relative(process.cwd(), filePath)}:`);
      opportunities.forEach(opp => {
        console.log(`  • ${opp.type}: ${opp.count} instances - ${opp.suggestion}`);
      });
    }
  });
  
  // Top optimization targets
  const highTokenFiles = analyses.filter(a => a.tokens > 1000);
  if (highTokenFiles.length > 0) {
    console.log(`\n🎯 Priority Optimization Targets (>1000 tokens):`);
    highTokenFiles.forEach(file => {
      console.log(`  • ${file.file} - ${file.tokens} tokens`);
    });
  }
  
  console.log(`\n✅ Analysis complete! Run weekly to track token usage trends.`);
}

// Weekly tracking function
function trackWeeklyUsage() {
  const promptPattern = path.join('..', 'shared-resources', 'prompts', '**', '*.md');
  const analyses = glob.sync(promptPattern).map(analyzePromptFile);
  const totalTokens = analyses.reduce((sum, a) => sum + a.tokens, 0);
  
  const logEntry = {
    date: new Date().toISOString().split('T')[0],
    totalTokens,
    fileCount: analyses.length,
    avgTokensPerFile: Math.round(totalTokens / analyses.length),
    topFiles: analyses.sort((a, b) => b.tokens - a.tokens).slice(0, 3).map(a => ({
      file: a.file,
      tokens: a.tokens
    }))
  };
  
  // Append to log file
  const logFile = 'scripts/token-usage-log.json';
  let logs = [];
  
  if (fs.existsSync(logFile)) {
    logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
  }
  
  logs.push(logEntry);
  fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
  
  console.log(`📝 Token usage logged for ${logEntry.date}`);
}

// Main execution
if (require.main === module) {
  const command = process.argv[2];
  
  if (command === 'track') {
    trackWeeklyUsage();
  } else {
    generateReport();
  }
}

module.exports = { estimateTokens, analyzePromptFile, findOptimizationOpportunities }; 