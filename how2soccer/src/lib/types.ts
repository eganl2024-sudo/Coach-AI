export interface Parent {
  id: string
  username: string
  email: string
  created_at: string
}

export interface Kid {
  id: string
  parent_id: string
  name: string
  age: number
  skill_level: 'beginner' | 'intermediate' | 'advanced'
  created_at: string
}

export type ChallengeRating = 'easy' | 'got_it' | 'tough'

export interface Progress {
  id: string
  kid_id: string
  challenge_id: string
  track: string
  completed_at: string
  stars: number
  rating: ChallengeRating | null
}

export type TrackId = 'juggling' | 'dribbling' | 'passing' | 'shooting'

export interface Challenge {
  id: string
  title: string
  description: string
  difficulty: 1 | 2 | 3
  tip: string
}

export interface Track {
  id: TrackId
  name: string
  emoji: string
  colorClass: string
  bgClass: string
  description: string
  challenges: Challenge[]
}

export interface Streak {
  id: string
  kid_id: string
  current_streak: number
  longest_streak: number
  last_practice_date: string | null
  timezone: string
}

export interface DailyMission {
  id: string
  kid_id: string
  challenge_id: string
  track: string
  date: string
  completed_at: string | null
}

export interface SessionData {
  parentId?: string
  parentUsername?: string
  kidId?: string
  kidName?: string
}
