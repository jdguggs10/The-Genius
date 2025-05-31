// Logger utility that respects environment and provides different log levels
class Logger {
  private isDev = import.meta.env.DEV;

  // Essential logs that should always appear (errors, important info)
  error(...args: any[]) {
    console.error(...args);
  }

  warn(...args: any[]) {
    console.warn(...args);
  }

  // Info logs that only appear in development
  info(...args: any[]) {
    if (this.isDev) {
      console.log(...args);
    }
  }

  // Debug logs that only appear in development (detailed SSE, etc.)
  debug(...args: any[]) {
    if (this.isDev) {
      console.log(...args);
    }
  }

  // Essential info that should appear in production (minimal, important status)
  essential(...args: any[]) {
    console.log(...args);
  }
}

export const logger = new Logger(); 