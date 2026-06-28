import { Track, TrackId, Challenge } from '../types'

export const TRACKS: Record<TrackId, Track> = {
  juggling: {
    id: 'juggling',
    name: 'Juggling',
    emoji: '⚽',
    colorClass: 'text-green-600',
    bgClass: 'bg-green-50 border-green-200',
    description: 'Keep the ball in the air!',
    challenges: [
      {
        id: 'jug-1',
        title: 'First Touch',
        description: 'Toss the ball up and kick it with your foot 1 time before catching it.',
        difficulty: 1,
        tip: 'Use the top of your foot and kick gently upward. Keep your ankle locked.',
      },
      {
        id: 'jug-2',
        title: 'Juggle 3',
        description: 'Keep the ball in the air for 3 touches in a row without letting it hit the ground.',
        difficulty: 1,
        tip: 'Try to hit the ball at the same height each time. Stay relaxed!',
      },
      {
        id: 'jug-3',
        title: 'Juggle 5',
        description: 'Keep the ball in the air for 5 touches in a row.',
        difficulty: 2,
        tip: 'Keep your eye on the ball and stay balanced. Use small kicks, not big ones.',
      },
      {
        id: 'jug-4',
        title: 'Juggle 10',
        description: 'Keep the ball in the air for 10 touches in a row.',
        difficulty: 2,
        tip: 'Relax your body! Tight muscles make juggling harder. Find your rhythm.',
      },
      {
        id: 'jug-5',
        title: 'Juggle 20',
        description: 'Keep the ball in the air for 20 touches in a row.',
        difficulty: 3,
        tip: 'Juggling is all about a steady beat. Count out loud to stay focused.',
      },
      {
        id: 'jug-6',
        title: 'Alternating Feet',
        description: 'Juggle 6 times alternating between your left and right foot each touch.',
        difficulty: 3,
        tip: 'Start slow — touch right, then left, then right. The rhythm is more important than speed.',
      },
      {
        id: 'jug-7',
        title: 'Thigh Juggle',
        description: 'Keep the ball in the air for 4 touches using only your thighs.',
        difficulty: 3,
        tip: 'Lift your knee to hip height and let the ball bounce off your flat thigh. Keep your upper body still.',
      },
      {
        id: 'jug-8',
        title: 'Juggle 30',
        description: 'Keep the ball in the air for 30 touches in a row using any part of your body.',
        difficulty: 3,
        tip: 'Mix in thighs and head to reset when you feel out of control. Survival over style!',
      },
    ],
  },
  dribbling: {
    id: 'dribbling',
    name: 'Dribbling',
    emoji: '🏃',
    colorClass: 'text-orange-600',
    bgClass: 'bg-orange-50 border-orange-200',
    description: 'Move with the ball at your feet!',
    challenges: [
      {
        id: 'dri-1',
        title: 'Right Foot Dribble',
        description: 'Dribble in a straight line for 10 yards using only your right foot.',
        difficulty: 1,
        tip: 'Use the inside and laces of your foot. Keep the ball close — no more than one step away.',
      },
      {
        id: 'dri-2',
        title: 'Left Foot Dribble',
        description: 'Dribble in a straight line for 10 yards using only your left foot.',
        difficulty: 1,
        tip: 'It feels weird at first — that is totally normal! The more you practice, the better it gets.',
      },
      {
        id: 'dri-3',
        title: 'Zigzag Dribble',
        description: 'Set up 5 cones or objects in a line and dribble through them in a zigzag pattern.',
        difficulty: 2,
        tip: 'Use the inside and outside of your foot to change direction quickly.',
      },
      {
        id: 'dri-4',
        title: 'Speed Dribble',
        description: 'Sprint with the ball under control for 20 yards without losing it.',
        difficulty: 2,
        tip: 'Push the ball a bit further ahead of you when sprinting so you can run faster.',
      },
      {
        id: 'dri-5',
        title: 'Stop & Go',
        description: 'Dribble forward, then stop the ball with the sole of your foot, then burst forward again. Do this 5 times.',
        difficulty: 3,
        tip: 'Put your foot flat on top of the ball to stop it cleanly, then explode forward.',
      },
      {
        id: 'dri-6',
        title: 'V-Cut',
        description: 'Dribble toward a cone, do a V-cut (pull ball back with sole, push sideways), then sprint away. Do this 5 times.',
        difficulty: 3,
        tip: 'The V-cut works because you fake going one way then cut the other. Sell the fake with your body!',
      },
      {
        id: 'dri-7',
        title: 'Step Over',
        description: 'Step over the ball (fake kick) with one foot, then push the ball the other direction. Do this move 5 times.',
        difficulty: 3,
        tip: 'Exaggerate the step over to make the defender think you\'re going the other way. Sell it!',
      },
      {
        id: 'dri-8',
        title: 'Figure 8',
        description: 'Set 2 cones 3 yards apart. Dribble in a figure-8 pattern around them 3 times without losing the ball.',
        difficulty: 3,
        tip: 'Use the inside and outside of both feet. Slow down on the tight turns — control beats speed here.',
      },
    ],
  },
  passing: {
    id: 'passing',
    name: 'Passing',
    emoji: '🦶',
    colorClass: 'text-blue-600',
    bgClass: 'bg-blue-50 border-blue-200',
    description: 'Share the ball with your teammates!',
    challenges: [
      {
        id: 'pas-1',
        title: 'Inside Foot Pass',
        description: 'Pass the ball against a wall or to a partner using the flat inside part of your foot.',
        difficulty: 1,
        tip: 'Point your toes up and turn your foot sideways. Strike through the middle of the ball.',
      },
      {
        id: 'pas-2',
        title: '5 in a Row',
        description: 'Complete 5 passes in a row against a wall or with a partner without a bad touch.',
        difficulty: 1,
        tip: 'Follow through toward your target after every kick. Aim for the same spot each time.',
      },
      {
        id: 'pas-3',
        title: '10 in a Row',
        description: 'Complete 10 passes in a row without a mistake.',
        difficulty: 2,
        tip: 'Pick a specific spot on the wall to aim for. Slow and accurate beats fast and sloppy.',
      },
      {
        id: 'pas-4',
        title: 'One-Touch Pass',
        description: 'When a partner or wall sends the ball back, pass it again with just one touch.',
        difficulty: 2,
        tip: 'Get your foot in position before the ball arrives so you are ready to pass immediately.',
      },
      {
        id: 'pas-5',
        title: 'Moving Pass',
        description: 'Jog forward and pass the ball accurately to a target or wall without stopping.',
        difficulty: 3,
        tip: 'Plant your non-kicking foot beside the ball and lean slightly over it when you kick.',
      },
      {
        id: 'pas-6',
        title: 'Outside Foot Pass',
        description: 'Pass the ball 5 times to a wall or partner using only the outside of your dominant foot.',
        difficulty: 3,
        tip: 'Point your toes inward and strike with the outside knuckle of your shoe. It feels strange at first!',
      },
      {
        id: 'pas-7',
        title: 'Long Accurate Pass',
        description: 'From 20 yards away, pass the ball and hit a target (cone, bag, or partner) 3 times out of 5.',
        difficulty: 3,
        tip: 'Lean over the ball and follow through straight toward your target. A lofted pass needs a firm but not powerful kick.',
      },
      {
        id: 'pas-8',
        title: 'Through Ball',
        description: 'Have a partner jog across in front of you. Pass the ball into the space ahead of them so they can run onto it.',
        difficulty: 3,
        tip: 'Pass to where they\'re going, not where they are. Think one step ahead!',
      },
    ],
  },
  shooting: {
    id: 'shooting',
    name: 'Shooting',
    emoji: '🥅',
    colorClass: 'text-red-600',
    bgClass: 'bg-red-50 border-red-200',
    description: 'Score goals and celebrate!',
    challenges: [
      {
        id: 'sho-1',
        title: 'Open Goal',
        description: 'Place the ball 5 yards from a goal (or two cones) and kick it in.',
        difficulty: 1,
        tip: 'Look at the goal first, then focus on the ball when you kick. Strike through the middle.',
      },
      {
        id: 'sho-2',
        title: 'Aim for the Corner',
        description: 'From 10 yards away, score by aiming for a corner of the goal.',
        difficulty: 2,
        tip: 'Pick your corner before you kick and commit to it — do not change your mind mid-run.',
      },
      {
        id: 'sho-3',
        title: 'Power Shot',
        description: 'From 15 yards, score with a powerful shot using the laces of your dominant foot.',
        difficulty: 2,
        tip: 'Lean over the ball and strike through the center with your laces for maximum power.',
      },
      {
        id: 'sho-4',
        title: 'Weak Foot Goal',
        description: 'Score from 10 yards using your weaker foot.',
        difficulty: 3,
        tip: 'Your weak foot just needs more practice. Slow it down — accuracy first, then add power.',
      },
      {
        id: 'sho-5',
        title: 'Moving Shot',
        description: 'Dribble toward the goal and shoot from a moving ball without stopping first.',
        difficulty: 3,
        tip: 'Take one big touch forward to set the ball, then plant and shoot in one smooth motion.',
      },
      {
        id: 'sho-6',
        title: 'Volley',
        description: 'Toss the ball into the air yourself and kick it before it hits the ground. Score 3 times.',
        difficulty: 3,
        tip: 'Watch the ball all the way onto your foot. Keep your ankle locked and your toes pointed down.',
      },
      {
        id: 'sho-7',
        title: 'Penalty Kick',
        description: 'From the penalty spot (12 yards), take 5 penalty kicks. Score at least 3 of them.',
        difficulty: 3,
        tip: 'Pick your spot before you start your run and commit — changing your mind mid-kick causes misses.',
      },
      {
        id: 'sho-8',
        title: 'Chip Shot',
        description: 'From 10 yards, chip the ball up and over a standing object (bag, cone stack, or partner\'s arms) into the goal.',
        difficulty: 3,
        tip: 'Stab the bottom of the ball with a short, sharp kick and don\'t follow through. Less is more!',
      },
    ],
  },
}

export const TRACK_IDS: TrackId[] = ['juggling', 'dribbling', 'passing', 'shooting']

export function getTrack(trackId: string): Track | undefined {
  return TRACKS[trackId as TrackId]
}

export function getChallenge(trackId: string, challengeId: string): Challenge | undefined {
  const track = getTrack(trackId)
  return track?.challenges.find((c) => c.id === challengeId)
}

export function getDifficultyLabel(difficulty: 1 | 2 | 3): string {
  return ['Beginner', 'Intermediate', 'Advanced'][difficulty - 1]
}
