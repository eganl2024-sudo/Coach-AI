import { describe, test, expect } from 'vitest'
import { getLevel } from '@/lib/utils/levels'

describe('getLevel', () => {
  test('0 stars → Rookie', () => expect(getLevel(0).name).toBe('Rookie'))
  test('4 stars → still Rookie (boundary)', () => expect(getLevel(4).name).toBe('Rookie'))
  test('5 stars → Player (tier up)', () => expect(getLevel(5).name).toBe('Player'))
  test('19 stars → Player (boundary)', () => expect(getLevel(19).name).toBe('Player'))
  test('20 stars → Pro', () => expect(getLevel(20).name).toBe('Pro'))
  test('39 stars → Pro (boundary)', () => expect(getLevel(39).name).toBe('Pro'))
  test('40 stars → Star', () => expect(getLevel(40).name).toBe('Star'))
  test('60 stars → Legend', () => expect(getLevel(60).name).toBe('Legend'))
  test('72 stars → Legend (max)', () => expect(getLevel(72).name).toBe('Legend'))

  test('Legend has no nextLevel', () => expect(getLevel(72).nextLevel).toBeNull())
  test('Rookie has nextLevel Player', () => expect(getLevel(0).nextLevel?.name).toBe('Player'))

  test('starsToNext is 5 at 0 stars (5 to Player)', () => expect(getLevel(0).starsToNext).toBe(5))
  test('starsToNext is 1 at 4 stars (1 more to Player)', () => expect(getLevel(4).starsToNext).toBe(1))
  test('starsToNext is 0 at max level', () => expect(getLevel(72).starsToNext).toBe(0))

  test('pct is between 0 and 100 for any valid star count', () => {
    for (let s = 0; s <= 72; s++) {
      const { pct } = getLevel(s)
      expect(pct).toBeGreaterThanOrEqual(0)
      expect(pct).toBeLessThanOrEqual(100)
    }
  })
})
