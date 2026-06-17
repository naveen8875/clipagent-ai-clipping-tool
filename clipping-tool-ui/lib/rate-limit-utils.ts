// Utility functions for rate limiting
export const RateLimitUtils = {
  // Check if rate limit is active (without setting it)
  isRateLimited: (action: string): boolean => {
    if (typeof window === "undefined") return false; // Server-side always allow

    const now = Date.now();
    const lastRequest = sessionStorage.getItem(`last_${action}_request`);

    if (lastRequest) {
      const timeDiff = now - parseInt(lastRequest);
      if (timeDiff < 60000) {
        // 60 seconds
        return true;
      }
    }

    return false;
  },

  // Check rate limit and set it if not limited (for actual requests)
  checkRateLimit: (action: string): boolean => {
    if (typeof window === "undefined") return true; // Server-side always allow

    const now = Date.now();
    const lastRequest = sessionStorage.getItem(`last_${action}_request`);

    if (lastRequest) {
      const timeDiff = now - parseInt(lastRequest);
      if (timeDiff < 60000) {
        // 60 seconds
        return false;
      }
    }

    sessionStorage.setItem(`last_${action}_request`, now.toString());
    return true;
  },

  getRemainingTime: (action: string): number => {
    if (typeof window === "undefined") return 0;

    const lastRequest = sessionStorage.getItem(`last_${action}_request`);
    if (!lastRequest) return 0;

    const timeDiff = Date.now() - parseInt(lastRequest);
    return Math.max(0, 60000 - timeDiff);
  },

  formatRemainingTime: (milliseconds: number): string => {
    const seconds = Math.ceil(milliseconds / 1000);
    return `${seconds} seconds`;
  },

  clearRateLimit: (action: string): void => {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(`last_${action}_request`);
  },
};
