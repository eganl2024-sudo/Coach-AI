const LEVELS = [
  { name: 'Rookie', emoji: '⚽', min: 0, max: 4 },
  { name: 'Player', emoji: '🏃', min: 5, max: 19 },
  { name: 'Pro', emoji: '⚡', min: 20, max: 39 },
  { name: 'Star', emoji: '🌟', min: 40, max: 59 },
  { name: 'Legend', emoji: '👑', min: 60, max: 72 },
] as const

type Level = (typeof LEVELS)[number]

export function getLevel(stars: number) {
  const idx = LEVELS.findIndex((l) => stars <= l.max)
  const level: Level = LEVELS[idx >= 0 ? idx : LEVELS.length - 1]
  const nextLevel: Level | null = idx >= 0 && idx < LEVELS.length - 1 ? LEVELS[idx + 1] : null

  const rangeSize = level.max - level.min + 1
  const pct = Math.min(100, Math.round(((stars - level.min) / rangeSize) * 100))

  return {
    name: level.name,
    emoji: level.emoji,
    nextLevel: nextLevel as { name: string; emoji: string; min: number } | null,
    pct,
    starsToNext: nextLevel ? nextLevel.min - stars : 0,
  }
}
