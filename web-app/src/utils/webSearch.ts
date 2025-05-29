export function shouldEnableWebSearch(input: string): boolean {
  const lowerInput = input.toLowerCase().trim();
  
  // Explicit search prefix
  if (lowerInput.startsWith('search:')) {
    return true;
  }
  
  // Time-sensitive keywords
  const timeKeywords = [
    'today', 'tonight', 'this week', 'this weekend', 'current', 'latest', 'recent',
    'now', 'live', 'active', 'injured', 'news', 'update', 'status'
  ];
  
  // Sports data keywords
  const sportsKeywords = [
    'stats', 'statistics', 'performance', 'points', 'scored', 'rushing', 'passing',
    'receiving', 'yards', 'touchdowns', 'interceptions', 'fumbles', 'targets',
    'carries', 'attempts', 'completions', 'qbr', 'rating', 'rank', 'rankings'
  ];
  
  // Team and schedule keywords
  const scheduleKeywords = [
    'plays', 'playing', 'vs', 'versus', 'against', 'matchup', 'opponent',
    'schedule', 'game', 'games', 'week', 'weather', 'conditions', 'forecast'
  ];
  
  // Injury and availability keywords
  const injuryKeywords = [
    'injury', 'injured', 'hurt', 'questionable', 'doubtful', 'out', 'inactive',
    'active', 'healthy', 'probable', 'ir', 'reserve', 'suspended', 'available'
  ];
  
  // Waiver and transaction keywords
  const transactionKeywords = [
    'waiver', 'waivers', 'pickup', 'drop', 'add', 'available', 'free agent',
    'trade', 'traded', 'released', 'signed', 'claim', 'claims'
  ];
  
  const allKeywords = [
    ...timeKeywords,
    ...sportsKeywords, 
    ...scheduleKeywords,
    ...injuryKeywords,
    ...transactionKeywords
  ];
  
  // Check if any keywords are present
  const hasRelevantKeywords = allKeywords.some(keyword => 
    lowerInput.includes(keyword)
  );
  
  // Check for question patterns that suggest real-time data need
  const questionPatterns = [
    /who (should|do|is|has|will)/,
    /what (is|are|happened|happens)/,
    /when (is|are|does|do)/,
    /how (is|are|did|has)/,
    /which (player|team)/
  ];
  
  const hasTimePattern = questionPatterns.some(pattern => 
    pattern.test(lowerInput)
  ) && hasRelevantKeywords;
  
  return hasRelevantKeywords || hasTimePattern;
}

export function getActualInput(input: string): string {
  // Remove 'search:' prefix if present
  if (input.toLowerCase().startsWith('search:')) {
    return input.slice(7).trim();
  }
  return input;
}

export function getSearchHint(input: string): string {
  const hasWebSearch = shouldEnableWebSearch(input);
  
  if (input.toLowerCase().startsWith('search:')) {
    return "🔍 Web search enabled (explicit)";
  }
  
  if (hasWebSearch) {
    return "🔍 Web search enabled (keywords detected)";
  }
  
  return "💬 Regular chat (add 'search:' for live data)";
} 