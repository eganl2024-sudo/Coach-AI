export const CATEGORIES = [
  'Warmup',
  'Technical',
  'Tactical',
  'Physical',
  'Game Application',
  'Cool Down',
] as const;

export type DrillCategory = typeof CATEGORIES[number];

export const CATEGORY_COLORS: Record<string, string> = {
  'Warmup':           'bg-orange-500/15 text-orange-400 border-orange-500/30',
  'Technical':        'bg-blue-500/15 text-blue-400 border-blue-500/30',
  'Tactical':         'bg-purple-500/15 text-purple-400 border-purple-500/30',
  'Physical':         'bg-red-500/15 text-red-400 border-red-500/30',
  'Game Application': 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  'Cool Down':        'bg-teal-500/15 text-teal-400 border-teal-500/30',
};

export const DIFFICULTY_COLORS: Record<string, string> = {
  'beginner':     'bg-green-500/15 text-green-400',
  'intermediate': 'bg-yellow-500/15 text-yellow-400',
  'advanced':     'bg-red-500/15 text-red-400',
};

export const INTENSITY_COLORS: Record<string, string> = {
  'low':    'bg-green-500',
  'medium': 'bg-yellow-400',
  'high':   'bg-red-500',
};
