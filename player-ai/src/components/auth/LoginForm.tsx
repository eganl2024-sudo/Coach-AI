'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { loginAction } from '@/lib/actions/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export default function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const err = params.get('error');
      if (err) {
        setError(err);
      }
    }
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await loginAction(username, password);
      if (result.success) {
        const params = new URLSearchParams(window.location.search);
        const next = params.get('next');
        router.push(next && next.startsWith('/') ? next : '/');
        router.refresh();
      } else {
        setError(result.error ?? 'Login failed.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4"
         style={{ background: 'radial-gradient(ellipse at top, #0d1f0f 0%, #0f1117 60%)' }}>
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-1">
          <div className="text-4xl font-black tracking-tight text-white font-display">
            Player AI
          </div>
          <p className="text-muted-foreground text-sm">
            Your personal soccer development platform
          </p>
        </div>

        <Card className="border-border/50 shadow-2xl">
          <CardHeader className="pb-2" />
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="e.g. alex_gk"
                  autoComplete="username"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    autoComplete="current-password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(p => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                    tabIndex={-1}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 4.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex justify-end">
                <Link href="/forgot-password" className="text-xs text-muted-foreground hover:text-primary transition-colors min-h-[44px] flex items-center">
                  Forgot password?
                </Link>
              </div>

              {error && (
                <p className="text-destructive text-sm text-center">{error}</p>
              )}

              <Button
                type="submit"
                className="w-full min-h-[44px] font-semibold"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="relative my-4 flex items-center justify-center">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border/50" />
              </div>
              <div className="relative flex justify-center text-xs uppercase z-10 bg-[#15171e] px-3">
                <span className="text-muted-foreground font-medium">Or</span>
              </div>
            </div>

            <Button
              variant="outline"
              type="button"
              className="w-full min-h-[44px] border-border/50 hover:bg-secondary/40 font-semibold flex items-center justify-center gap-2 cursor-pointer transition-all duration-200"
              onClick={() => {
                router.push('/api/auth/google');
              }}
            >
              <svg className="size-4 mr-1" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              Continue with Google
            </Button>
          </CardContent>
        </Card>

        <div className="flex items-center justify-center min-h-[44px] text-xs text-muted-foreground text-center">
          New here?{' '}
          <Link href="/signup" className="text-primary hover:underline font-medium ml-1">
            Create a free account →
          </Link>
        </div>

        <div className="flex items-center justify-center gap-3 min-h-[44px] text-xs text-muted-foreground/60">
          <Link href="/terms" className="hover:text-muted-foreground underline py-2">Terms</Link>
          <span>·</span>
          <Link href="/privacy" className="hover:text-muted-foreground underline py-2">Privacy</Link>
        </div>
      </div>
    </div>
  );
}
