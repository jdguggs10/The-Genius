import { useState } from "react";

const MAX_DAILY_MESSAGES = 5;

export function useDailyQuota() {
  const today = new Date().toISOString().slice(0, 10); // Format: YYYY-MM-DD
  const storageKey = `quota-${today}`;
  
  // Get the current count from localStorage
  const [count, setCount] = useState(() => {
    return parseInt(localStorage.getItem(storageKey) || '0');
  });
  
  // Function to increment the count
  const increment = () => {
    const newCount = count + 1;
    localStorage.setItem(storageKey, String(newCount));
    setCount(newCount);
  };
  
  return {
    count,
    increment,
    limit: MAX_DAILY_MESSAGES,
    isLimitReached: count >= MAX_DAILY_MESSAGES
  };
}