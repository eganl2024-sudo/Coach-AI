/**
 * Structured security logger.
 *
 * Emits newline-delimited JSON to stdout. On Vercel, stdout is automatically
 * ingested by the log drain; on other hosts it is captured by the process
 * supervisor. Never log passwords, tokens, full emails, or raw error stacks.
 *
 * High-severity events are also forwarded to Sentry via captureEvent so they
 * appear in the Sentry Issues feed and can trigger alerts.
 */

type Level = 'info' | 'warn' | 'error';

interface LogEntry {
  ts: string;
  level: Level;
  event: string;
  username?: string;
  [key: string]: unknown;
}

function emit(level: Level, event: string, fields: Record<string, unknown> = {}): void {
  const entry: LogEntry = {
    ts: new Date().toISOString(),
    level,
    event,
    ...fields,
  };
  const line = JSON.stringify(entry);
  if (level === 'error') {
    console.error(line);
  } else if (level === 'warn') {
    console.warn(line);
  } else {
    console.log(line);
  }

  // Forward high-severity events to Sentry (non-blocking, best-effort).
  if (level === 'error' || level === 'warn') {
    try {
      // Dynamic import keeps this out of the critical path and avoids the
      // Sentry SDK being bundled into every edge/server chunk unnecessarily.
      import('@sentry/nextjs').then(({ captureEvent }) => {
        captureEvent({
          level: level === 'error' ? 'error' : 'warning',
          message: event,
          tags: { security: 'true' },
          extra: fields,
        });
      }).catch(() => { /* Sentry unavailable — swallow silently */ });
    } catch {
      // Sentry not installed or initialised — no-op.
    }
  }
}

// ── Auth events ────────────────────────────────────────────────────────────

export const log = {
  /** Successful login */
  loginSuccess(username: string) {
    emit('info', 'auth.login.success', { username });
  },

  /** Failed login — bad credentials */
  loginFailure(username: string) {
    emit('warn', 'auth.login.failure', { username });
  },

  /** Login blocked by rate limiter */
  loginRateLimited(username: string) {
    emit('warn', 'auth.login.rate_limited', { username });
  },

  /** New account created successfully */
  signupSuccess(username: string) {
    emit('info', 'auth.signup.success', { username });
  },

  /** Signup blocked by global rate limiter */
  signupRateLimited() {
    emit('warn', 'auth.signup.rate_limited');
  },

  /** Honeypot field was filled — bot detected */
  signupHoneypot() {
    emit('warn', 'auth.signup.honeypot_triggered');
  },

  /** Password reset email requested */
  passwordResetRequested(username: string) {
    emit('info', 'auth.password_reset.requested', { username });
  },

  /** Password reset confirmation submitted */
  passwordResetConfirmed() {
    emit('info', 'auth.password_reset.confirmed');
  },

  /** Reset confirmation blocked by rate limiter — possible token brute-force */
  passwordResetRateLimited() {
    emit('error', 'auth.password_reset.rate_limited');
  },

  /** Password changed successfully by an authenticated user */
  passwordChanged(username: string) {
    emit('info', 'auth.password.changed', { username });
  },

  /** Password change blocked by rate limiter */
  passwordChangeRateLimited(username: string) {
    emit('warn', 'auth.password.rate_limited', { username });
  },

  /** Account deleted */
  accountDeleted(username: string) {
    emit('info', 'auth.account.deleted', { username });
  },

  /** Account deletion blocked by rate limiter */
  accountDeleteRateLimited(username: string) {
    emit('warn', 'auth.account.rate_limited', { username });
  },

  // ── Admin events ──────────────────────────────────────────────────────────

  /** Admin panel login succeeded — always notable */
  adminLoginSuccess() {
    emit('warn', 'auth.admin.login_success');
  },

  /** Admin panel login failed — wrong password */
  adminLoginFailure() {
    emit('warn', 'auth.admin.login_failure');
  },

  /** Admin panel login blocked — active brute-force attempt */
  adminLoginRateLimited() {
    emit('error', 'auth.admin.rate_limited');
  },

  // ── Resource events ───────────────────────────────────────────────────────

  /** Reel upload blocked by rate limiter */
  reelUploadRateLimited(username: string) {
    emit('warn', 'reel.upload.rate_limited', { username });
  },

  /** Review submission blocked by rate limiter */
  reelSubmitRateLimited(username: string) {
    emit('warn', 'reel.submit.rate_limited', { username });
  },

  // ── API events ────────────────────────────────────────────────────────────

  /** Unhandled error in an API route or server action */
  apiError(route: string, err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    emit('error', 'api.error', { route, message });
  },

  /** AI generation blocked by rate limiter */
  aiRateLimited(username: string) {
    emit('warn', 'ai.draft_email.rate_limited', { username });
  },
};
