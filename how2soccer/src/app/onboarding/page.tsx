'use client'

import { useState, useTransition } from 'react'
import { addKidAction } from '@/lib/actions/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

const SKILL_LEVELS = [
  { value: 'beginner', label: 'Just Starting Out', emoji: '🌱', desc: 'Brand new to soccer' },
  { value: 'intermediate', label: 'Getting Better', emoji: '⚡', desc: 'Played a season or two' },
  { value: 'advanced', label: 'Loves the Game', emoji: '🔥', desc: 'Plays regularly' },
]

export default function OnboardingPage() {
  const [skillLevel, setSkillLevel] = useState('beginner')
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    formData.set('skill_level', skillLevel)
    startTransition(async () => {
      const result = await addKidAction(formData)
      if (result?.error) setError(result.error)
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">👟</div>
          <h1 className="text-2xl font-black text-gray-900">Set Up Your Player</h1>
          <p className="text-gray-500 mt-1">Tell us about your young soccer star!</p>
        </div>

        <div className="bg-white rounded-3xl border-2 border-gray-100 p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="name">Player&apos;s First Name</Label>
              <Input
                id="name"
                name="name"
                type="text"
                placeholder="e.g. Jamie"
                required
                maxLength={50}
              />
            </div>

            <div>
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                name="age"
                type="number"
                min={4}
                max={13}
                placeholder="e.g. 8"
                required
              />
            </div>

            <div>
              <Label>Skill Level</Label>
              <div className="space-y-2 mt-1">
                {SKILL_LEVELS.map((level) => (
                  <button
                    key={level.value}
                    type="button"
                    onClick={() => setSkillLevel(level.value)}
                    className={cn(
                      'w-full flex items-center gap-3 p-3 rounded-xl border-2 text-left transition-all',
                      skillLevel === level.value
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300',
                    )}
                  >
                    <span className="text-2xl">{level.emoji}</span>
                    <div>
                      <p className="font-semibold text-gray-900 text-sm">{level.label}</p>
                      <p className="text-xs text-gray-500">{level.desc}</p>
                    </div>
                    {skillLevel === level.value && (
                      <span className="ml-auto text-green-500 font-bold">✓</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-xl px-4 py-3 text-sm text-red-600 font-medium">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" size="lg" disabled={isPending}>
              {isPending ? 'Setting up…' : "Let's Go! 🚀"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
