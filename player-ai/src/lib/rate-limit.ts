/**
 * Sliding-window in-memory rate limiter.
 *
 * Works per serverless instance. Sufficient to prevent burst abuse on
 * single-instance or low-traffic deployments. Upgrade to
 * @upstash/ratelimit backed by Redis for cross-instance enforcement.
 */

interface Window {
  tokens: number;
  lastRefill: number;
}

const store = new Map<string, Window>();

// Prevent unbounded memory growth on long-lived processes.
// Runs at most once every 10 minutes; removes windows that have fully expired.
let _lastCleanup = Date.now();
function _maybeCleanup(windowMs: number): void {
  const now = Date.now();
  if (now - _lastCleanup < 10 * 60 * 1000) return;
  _lastCleanup = now;
  for (const [key, win] of store.entries()) {
    if (now - win.lastRefill >= windowMs) store.delete(key);
  }
}

export interface RateLimitOptions {
  /** Max requests allowed in the window */
  limit: number;
  /** Window duration in milliseconds */
  windowMs: number;
}

export interface RateLimitResult {
  /** true = request is allowed */
  allowed: boolean;
  /** Remaining tokens after this request (0 when blocked) */
  remaining: number;
  /** Seconds until the window resets */
  retryAfterSeconds: number;
}

/**
 * Returns true if the request should be allowed, false if rate-limited.
 * `key` should be unique per user+action, e.g. `draft-email:username`.
 */
export function checkRateLimit(key: string, options: RateLimitOptions): boolean {
  return checkRateLimitWithInfo(key, options).allowed;
}

/**
 * Like checkRateLimit but also returns remaining tokens and retry-after
 * so callers can populate X-RateLimit-* response headers.
 */
export function checkRateLimitWithInfo(
  key: string,
  options: RateLimitOptions,
): RateLimitResult {
  _maybeCleanup(options.windowMs);
  const now = Date.now();
  const existing = store.get(key);

  if (!existing) {
    store.set(key, { tokens: options.limit - 1, lastRefill: now });
    return { allowed: true, remaining: options.limit - 1, retryAfterSeconds: 0 };
  }

  const elapsed = now - existing.lastRefill;

  if (elapsed >= options.windowMs) {
    store.set(key, { tokens: options.limit - 1, lastRefill: now });
    return { allowed: true, remaining: options.limit - 1, retryAfterSeconds: 0 };
  }

  if (existing.tokens > 0) {
    existing.tokens -= 1;
    return { allowed: true, remaining: existing.tokens, retryAfterSeconds: 0 };
  }

  const retryAfterSeconds = Math.ceil((options.windowMs - elapsed) / 1000);
  return { allowed: false, remaining: 0, retryAfterSeconds };
}
