'use client'

import { useState, useTransition } from 'react'
import Link from 'next/link'
import { loginAction } from '@/lib/actions/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export function LoginForm() {
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    startTransition(async () => {
      const result = await loginAction(formData)
      if (result?.error) setError(result.error)
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">⚽</div>
          <h1 className="text-3xl font-black text-green-600 tracking-tight">How 2 Soccer</h1>
          <p className="text-gray-500 mt-1">Welcome back, coach!</p>
        </div>

        <div className="bg-white rounded-3xl border-2 border-gray-100 p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="your_username"
                autoCapitalize="none"
                autoCorrect="off"
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-xl px-4 py-3 text-sm text-red-600 font-medium">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" size="lg" disabled={isPending}>
              {isPending ? 'Signing in…' : 'Sign In'}
            </Button>
          </form>
        </div>

        <p className="text-center text-gray-500 mt-6">
          New here?{' '}
          <Link href="/signup" className="text-green-600 font-semibold hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  )
}
