import { describe, test, expect } from 'vitest'
import { getUnlockedChallengeIds, TRACKS, TRACK_IDS } from '@/lib/data/curriculum'

// Use all tracks so we catch any curriculum shape that breaks the unlock logic
for (const trackId of TRACK_IDS) {
  const track = TRACKS[trackId]
  const tier1 = track.challenges.filter((c) => c.difficulty === 1)
  const tier2 = track.challenges.filter((c) => c.difficulty === 2)
  const tier3 = track.challenges.filter((c) => c.difficulty === 3)
  const tier1Ids = new Set(tier1.map((c) => c.id))
  const tier1And2Ids = new Set(track.challenges.filter((c) => c.difficulty <= 2).map((c) => c.id))

  describe(`getUnlockedChallengeIds — ${trackId}`, () => {
    test('tier 1 unlocked with no completions', () => {
      const unlocked = getUnlockedChallengeIds(track, new Set())
      tier1.forEach((c) => expect(unlocked.has(c.id)).toBe(true))
    })

    test('tier 2 locked with no completions', () => {
      if (tier2.length === 0) return
      const unlocked = getUnlockedChallengeIds(track, new Set())
      tier2.forEach((c) => expect(unlocked.has(c.id)).toBe(false))
    })

    test('tier 2 unlocks when all tier 1 done', () => {
      if (tier2.length === 0) return
      const unlocked = getUnlockedChallengeIds(track, tier1Ids)
      tier2.forEach((c) => expect(unlocked.has(c.id)).toBe(true))
    })

    test('tier 3 stays locked when only tier 1 done', () => {
      if (tier3.length === 0) return
      const unlocked = getUnlockedChallengeIds(track, tier1Ids)
      tier3.forEach((c) => expect(unlocked.has(c.id)).toBe(false))
    })

    test('tier 3 unlocks when tier 1 and 2 complete', () => {
      if (tier3.length === 0) return
      const unlocked = getUnlockedChallengeIds(track, tier1And2Ids)
      tier3.forEach((c) => expect(unlocked.has(c.id)).toBe(true))
    })

    test('partial tier 1 completion does not unlock tier 2', () => {
      if (tier1.length < 2 || tier2.length === 0) return
      const partial = new Set([tier1[0].id]) // only first tier-1 challenge done
      const unlocked = getUnlockedChallengeIds(track, partial)
      tier2.forEach((c) => expect(unlocked.has(c.id)).toBe(false))
    })
  })
}
