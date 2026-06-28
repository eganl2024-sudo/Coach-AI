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

export interface Progress {
  id: string
  kid_id: string
  challenge_id: string
  track: string
  completed_at: string
  stars: number
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

export interface SessionData {
  parentId?: string
  parentUsername?: string
  kidId?: string
  kidName?: string
}
