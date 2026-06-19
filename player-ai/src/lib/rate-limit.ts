/**
 * Sliding-window in-memory rate limiter.
 *
 * Works per serverless instance. Sufficient to prevent burst abuse; upgrade to
 * Upstash Redis (@upstash/ratelimit) if you need cross-instance enforcement.
 */

interface Window {
  tokens: number;
  lastRefill: number;
}

const store = new Map<string, Window>();

export interface RateLimitOptions {
  /** Max requests allowed in the window */
  limit: number;
  /** Window duration in milliseconds */
  windowMs: number;
}

/**
 * Returns true if the request should be allowed, false if rate-limited.
 * `key` should be unique per user+action, e.g. `draft-email:username`.
 */
export function checkRateLimit(key: string, options: RateLimitOptions): boolean {
  const now = Date.now();
  const existing = store.get(key);

  if (!existing) {
    store.set(key, { tokens: options.limit - 1, lastRefill: now });
    return true;
  }

  const elapsed = now - existing.lastRefill;

  if (elapsed >= options.windowMs) {
    // Window has expired — reset
    store.set(key, { tokens: options.limit - 1, lastRefill: now });
    return true;
  }

  if (existing.tokens > 0) {
    existing.tokens -= 1;
    return true;
  }

  return false;
}
