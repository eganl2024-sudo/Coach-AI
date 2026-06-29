/**
 * IDOR guard tests: each server action must reject a kidId that doesn't match
 * the session, returning an empty result without hitting the DB.
 */
import { describe, test, expect, vi, beforeEach } from 'vitest'

vi.mock('@/lib/session', () => ({ getSession: vi.fn() }))
// supabase should never be called on the IDOR path — mock it so a real call would throw
vi.mock('@/lib/supabase/server', () => ({
  createServerClient: vi.fn(() => {
    throw new Error('DB should not be reached on IDOR path')
  }),
}))
// completeDailyMission is imported by progress.ts
vi.mock('next/cache', () => ({ revalidatePath: vi.fn() }))

import { getSession } from '@/lib/session'

const REAL_KID = 'real-kid-id'
const ATTACKER_KID = 'attacker-kid-id'

type MockSession = { kidId?: string; parentId?: string; save: () => Promise<void>; destroy: () => void }
const mockSession = (kidId?: string): MockSession => ({
  kidId,
  save: vi.fn(),
  destroy: vi.fn(),
})

beforeEach(() => {
  vi.mocked(getSession).mockResolvedValue(mockSession(REAL_KID) as never)
})

describe('getTodaysMissions — IDOR guard', () => {
  test('returns [] for mismatched kidId', async () => {
    const { getTodaysMissions } = await import('@/lib/actions/missions')
    const result = await getTodaysMissions(ATTACKER_KID)
    expect(result).toEqual([])
  })
})

describe('getKidProgress — IDOR guard', () => {
  test('returns [] for mismatched kidId', async () => {
    const { getKidProgress } = await import('@/lib/actions/progress')
    const result = await getKidProgress(ATTACKER_KID)
    expect(result).toEqual([])
  })
})

describe('getWeekActivity — IDOR guard', () => {
  test('returns all-inactive days for mismatched kidId (no DB call)', async () => {
    const { getWeekActivity } = await import('@/lib/actions/progress')
    const result = await getWeekActivity(ATTACKER_KID)
    expect(result).toHaveLength(7)
    expect(result.every((d) => !d.active)).toBe(true)
  })
})

describe('getStreak — IDOR guard', () => {
  test('returns null for mismatched kidId', async () => {
    const { getStreak } = await import('@/lib/actions/streaks')
    const result = await getStreak(ATTACKER_KID)
    expect(result).toBeNull()
  })
})
