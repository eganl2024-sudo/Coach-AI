'use client';

import { useState } from 'react';
import Link from 'next/link';
import { requestPasswordResetAction } from '@/lib/actions/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export default function ForgotPasswordForm() {
  const [username, setUsername] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await requestPasswordResetAction(username);
      // Always show success — never reveal whether the account exists
      setSubmitted(true);
    } catch {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4"
         style={{ background: 'radial-gradient(ellipse at top, #0d1f0f 0%, #0f1117 60%)' }}>
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <div className="text-4xl font-black tracking-tight text-white select-none">
            Player AI
          </div>
          <p className="text-muted-foreground text-sm">Reset your password</p>
        </div>

        <Card className="border-border/50 shadow-2xl">
          <CardHeader className="pb-2" />
          <CardContent>
            {submitted ? (
              <div className="text-center space-y-4 py-2">
                <p className="text-sm text-muted-foreground">
                  If that username has an email address on file, we&apos;ve sent a reset link.
                  Check your inbox — the link expires in <strong className="text-foreground">1 hour</strong>.
                </p>
                <Link href="/login">
                  <Button variant="outline" className="w-full mt-2">Back to Sign In</Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Your username"
                    autoComplete="username"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Enter the username you signed up with. If an email is on file, we&apos;ll send a reset link.
                  </p>
                </div>

                {error && <p className="text-destructive text-sm text-center">{error}</p>}

                <Button type="submit" className="w-full font-semibold" disabled={loading}>
                  {loading ? 'Sending...' : 'Send Reset Link'}
                </Button>

                <p className="text-center text-xs text-muted-foreground">
                  <Link href="/login" className="text-primary hover:underline">← Back to Sign In</Link>
                </p>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
