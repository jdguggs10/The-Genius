export const shouldEnableWebSearch = (inputText: string): boolean => {
  const inputLower = inputText.toLowerCase();

  if (inputLower.startsWith('search:')) {
    return true;
  }

  const webSearchKeywords = [
    'stats', 'current', 'latest', 'today', 'now', 'recent', 'this week',
    'who plays', 'schedule', 'game', 'match', 'upcoming', 'when',
    'injury report', 'news', 'update', 'status', 'live', 'real-time',
    'search', 'find', 'look up', 'check', 'what happened'
  ];

  const searchPhrases = [
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
  ];

  const hasKeyword = webSearchKeywords.some(keyword => inputLower.includes(keyword));
  const hasPhrase = searchPhrases.some(phrase => inputLower.includes(phrase));

  return hasKeyword || hasPhrase;
};

export const getActualInput = (inputText: string): string => {
  if (inputText.toLowerCase().startsWith('search:')) {
    return inputText.slice(7).trim();
  }
  return inputText;
}; 