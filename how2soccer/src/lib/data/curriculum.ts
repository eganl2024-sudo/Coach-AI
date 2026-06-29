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
      // Beginner (3)
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
        id: 'jug-9',
        title: 'Bounce & Kick',
        description: 'Drop the ball, let it bounce once, then kick it back up before it bounces again. Catch it. Do this 5 times in a row.',
        difficulty: 1,
        tip: 'Time your kick for just after the bounce — that is when the ball is easiest to control.',
      },
      // Intermediate (4)
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
        id: 'jug-10',
        title: 'Juggle 15',
        description: 'Keep the ball in the air for 15 touches in a row.',
        difficulty: 2,
        tip: 'Count out loud — hearing the numbers helps you stay focused and builds rhythm.',
      },
      {
        id: 'jug-11',
        title: 'Head Touch',
        description: 'Toss the ball into the air, head it gently upward, then catch it. Do 5 headers in a row.',
        difficulty: 2,
        tip: 'Use your forehead — not the top of your head. Keep your eyes open and neck firm.',
      },
      // Advanced (5)
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
      {
        id: 'jug-12',
        title: 'Around the World',
        description: 'Juggle the ball, swing your foot all the way around it without touching it, then continue juggling. Do this 3 times.',
        difficulty: 3,
        tip: 'Juggle a few touches first to get your rhythm, then swing your foot in a full circle as the ball is in the air.',
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
      // Beginner (3)
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
        id: 'dri-9',
        title: 'Two-Foot Dribble',
        description: 'Dribble 15 yards using both feet, switching which foot touches the ball every 2-3 steps.',
        difficulty: 1,
        tip: 'Think left-left-right-right as you go. Nice and controlled beats fast and sloppy.',
      },
      // Intermediate (4)
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
        id: 'dri-10',
        title: 'Pull-Back Turn',
        description: 'Dribble toward a cone, use the sole of your foot to pull the ball back, then turn and dribble the other way. Do 5 turns.',
        difficulty: 2,
        tip: 'Stop the ball with the sole flat on top, then roll it behind you. Step around it quickly.',
      },
      {
        id: 'dri-11',
        title: 'Outside Foot Dribble',
        description: 'Dribble 15 yards using only the outside of your dominant foot.',
        difficulty: 2,
        tip: 'Turn your toes slightly inward so the outside of your foot can guide the ball. Small touches!',
      },
      // Advanced (5)
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
      {
        id: 'dri-12',
        title: 'Random Cone Run',
        description: 'Set up 6 cones anywhere in a 10x10 yard area. Dribble to touch every cone in any order as fast as you can. Do it twice.',
        difficulty: 3,
        tip: 'Look up to plan your next cone while the ball is rolling. The best dribblers always see ahead.',
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
      // Beginner (3)
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
        id: 'pas-9',
        title: 'Soft Pass',
        description: 'From 5 yards, pass the ball gently enough that it rolls all the way to your target without bouncing. 5 times.',
        difficulty: 1,
        tip: 'Cushion your kick — just enough power to reach. Too hard and you lose control, too soft and it stops short.',
      },
      // Intermediate (4)
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
        id: 'pas-10',
        title: 'Driven Pass',
        description: 'From 15 yards, pass the ball hard and flat to hit a cone or target. Score 5 hits out of 7 tries.',
        difficulty: 2,
        tip: 'Lock your ankle firm and follow through straight toward the target. Plant your non-kicking foot beside the ball.',
      },
      {
        id: 'pas-11',
        title: 'Two-Foot Combo',
        description: 'Pass 3 times with your right foot, then 3 times with your left foot. Complete 2 full rounds without a miss.',
        difficulty: 2,
        tip: 'Your weaker foot will feel awkward — slow it down and focus on contact before adding speed.',
      },
      // Advanced (5)
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
      {
        id: 'pas-12',
        title: 'Switch Play',
        description: 'Stand in the center. Pass to a cone on your left, sprint right, receive a pass (or wall return) on your right side. 5 reps.',
        difficulty: 3,
        tip: 'The moment you pass, start moving. Great players pass and go — never pass and stand.',
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
      // Beginner (3)
      {
        id: 'sho-1',
        title: 'Open Goal',
        description: 'Place the ball 5 yards from a goal (or two cones) and kick it in.',
        difficulty: 1,
        tip: 'Look at the goal first, then focus on the ball when you kick. Strike through the middle.',
      },
      {
        id: 'sho-9',
        title: 'Toe Poke',
        description: 'From 5 yards, score a goal using a toe poke — poking the ball with the very tip of your shoe.',
        difficulty: 1,
        tip: 'Keep your knee over the ball and jab quickly. Toe pokes are faster than a full swing — surprise the keeper!',
      },
      {
        id: 'sho-10',
        title: 'Both Feet',
        description: 'Score 1 goal with your right foot and 1 goal with your left foot from 8 yards.',
        difficulty: 1,
        tip: 'Your weaker foot just needs more chances. Slow your run-up down when using it.',
      },
      // Intermediate (4)
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
        id: 'sho-11',
        title: 'Low & High',
        description: 'From 10 yards, score once with a low shot that stays below knee height, then once with a high shot. 2 goals total.',
        difficulty: 2,
        tip: 'For low: lean over the ball and strike through the middle. For high: lean back slightly and get under it.',
      },
      {
        id: 'sho-12',
        title: 'Instep Drive',
        description: 'From 12 yards, strike the ball with your laces and score with pace. Score 3 out of 5 shots.',
        difficulty: 2,
        tip: 'A good instep drive is all about a locked ankle and following through. Lean over the ball so it stays low.',
      },
      // Advanced (5)
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
  control: {
    id: 'control',
    name: 'Ball Control',
    emoji: '🎯',
    colorClass: 'text-purple-600',
    bgClass: 'bg-purple-50 border-purple-200',
    description: 'Receive the ball like a pro!',
    challenges: [
      // Beginner (3)
      {
        id: 'ctl-1',
        title: 'Sole Roll',
        description: 'Roll the ball forward with the sole of your foot for 5 yards, then roll it back. Do 5 reps each foot.',
        difficulty: 1,
        tip: 'Keep the ball under the flat part of your foot. Light touch — you\'re rolling it, not kicking it.',
      },
      {
        id: 'ctl-2',
        title: 'Inside Trap',
        description: 'Roll a ball toward yourself (or have a partner pass it), and stop it dead using the inside of your foot. 10 times.',
        difficulty: 1,
        tip: 'Meet the ball as it arrives and cushion it — like catching an egg. Ease into the stop, don\'t stab.',
      },
      {
        id: 'ctl-3',
        title: 'Sole Trap',
        description: 'Have a partner roll the ball toward you and stop it cleanly using the sole of your foot before it passes you. 10 times.',
        difficulty: 1,
        tip: 'Put your foot slightly in front of the ball and press down gently as it arrives. Lift your toes!',
      },
      // Intermediate (4)
      {
        id: 'ctl-4',
        title: 'Chest Down',
        description: 'Toss the ball into the air, let it hit your chest, and cushion it down to your feet. Do 5 times without it bouncing away.',
        difficulty: 2,
        tip: 'Lean back a little and puff your chest out. As the ball hits, pull back to absorb it.',
      },
      {
        id: 'ctl-5',
        title: 'Thigh Control',
        description: 'Toss the ball up and trap it cleanly on your thigh so it drops gently to your feet. 5 times.',
        difficulty: 2,
        tip: 'Raise your knee so your thigh is flat. Pull your thigh downward as the ball arrives to kill its pace.',
      },
      {
        id: 'ctl-6',
        title: 'Wall Control',
        description: 'Pass to a wall and control the return ball before it bounces twice. 10 reps in a row without a mistake.',
        difficulty: 2,
        tip: 'Get your body in line with the ball early. Great first touches start with great positioning.',
      },
      {
        id: 'ctl-7',
        title: 'Trap and Turn',
        description: 'Receive a rolled ball with your back to target, trap it, and turn to face the opposite direction. 5 smooth turns.',
        difficulty: 2,
        tip: 'Trap first, then turn. Don\'t rush the turn — a clean trap is more important than a fast turn.',
      },
      // Advanced (5)
      {
        id: 'ctl-8',
        title: 'First Touch Forward',
        description: 'Control a pass so that your very first touch moves the ball in the direction you want to go. 8 reps.',
        difficulty: 3,
        tip: 'Angle your foot before contact so the ball deflects forward. This is what separates good players from great ones.',
      },
      {
        id: 'ctl-9',
        title: 'Laces Control',
        description: 'Trap a ball tossed at waist height using the top of your foot (laces), cushioning it gently to the ground. 5 times.',
        difficulty: 3,
        tip: 'Drop your leg down as the ball arrives to absorb the pace. Keep your ankle relaxed, not locked.',
      },
      {
        id: 'ctl-10',
        title: 'Outside of Foot',
        description: 'Control 5 passes using only the outside of your foot, keeping the ball within arm\'s reach after each trap.',
        difficulty: 3,
        tip: 'Angle your foot so the outside edge faces the ball. This is great for quick changes of direction!',
      },
      {
        id: 'ctl-11',
        title: 'Weak Foot Control',
        description: 'Control 5 passes in a row using only your weaker foot, keeping the ball within 1 yard of you each time.',
        difficulty: 3,
        tip: 'Slow the pass down if needed. Weak foot control is built by repetition — give it more chances!',
      },
      {
        id: 'ctl-12',
        title: 'Speed Control',
        description: 'Control a pass, take one touch, and play it back to your target in under 3 seconds. 10 reps without losing the ball.',
        difficulty: 3,
        tip: 'Your first touch should set up your second touch. Think two moves ahead before the ball even arrives.',
      },
    ],
  },
  tricks: {
    id: 'tricks',
    name: 'Tricks',
    emoji: '✨',
    colorClass: 'text-pink-600',
    bgClass: 'bg-pink-50 border-pink-200',
    description: 'Learn the moves that wow the crowd!',
    challenges: [
      // Beginner (3)
      {
        id: 'trk-1',
        title: 'Toe Taps',
        description: 'Tap the top of the ball alternating between your left and right foot as fast as you can. 20 taps total.',
        difficulty: 1,
        tip: 'Stay on the balls of your feet and keep your knees slightly bent. Light, quick taps — not heavy stomps.',
      },
      {
        id: 'trk-2',
        title: 'Inside-Outside Touch',
        description: 'Touch the ball with the inside of your foot, then push it sideways with the outside of the same foot. 10 times each foot.',
        difficulty: 1,
        tip: 'This is the foundation of every big move. Inside touches point inward, outside touches use your little toe side.',
      },
      {
        id: 'trk-3',
        title: 'Ball Roll',
        description: 'Roll the ball sideways with the sole of one foot, stop it with the other foot. 10 times each direction.',
        difficulty: 1,
        tip: 'Keep your eyes on the ball and use a light rolling touch. Great for warming up your feet!',
      },
      // Intermediate (4)
      {
        id: 'trk-4',
        title: 'Step Over',
        description: 'Swing your foot over the ball without touching it (a big fake), then push the ball in the opposite direction. 5 times each foot.',
        difficulty: 2,
        tip: 'Exaggerate the step over — lean your body the wrong way to sell the fake, then burst the other way.',
      },
      {
        id: 'trk-5',
        title: 'Scissors',
        description: 'Swing one foot around the ball, then the other in the opposite direction (full scissors). Burst away. 5 times.',
        difficulty: 2,
        tip: 'Right foot swings right-to-left, then left foot swings left-to-right, then go! It\'s a one-two rhythm.',
      },
      {
        id: 'trk-6',
        title: 'Drag Back',
        description: 'While dribbling forward, suddenly stop the ball with the sole of your foot and drag it back behind you. 5 times.',
        difficulty: 2,
        tip: 'Plant your non-dragging foot to stop your momentum. The drag-back is a quick change of direction tool.',
      },
      {
        id: 'trk-7',
        title: 'Heel Flick',
        description: 'Roll the ball forward with the sole of your foot, then flick it back with your heel before it rolls away. 5 times.',
        difficulty: 2,
        tip: 'Roll it gently so the ball is still close when you flick back. The flick is quick — don\'t wind up.',
      },
      // Advanced (5)
      {
        id: 'trk-8',
        title: 'Cruyff Turn',
        description: 'Fake a pass or shot, then drag the ball behind your standing leg with the inside of your foot and spin away. 5 times.',
        difficulty: 3,
        tip: 'The bigger the fake, the better the turn. Plant, fake, then drag behind in one quick motion.',
      },
      {
        id: 'trk-9',
        title: 'Roulette',
        description: 'Roll the ball forward with one foot, spin your body 360°, and stop the ball with the other foot. 3 times each way.',
        difficulty: 3,
        tip: 'Roll, then immediately start spinning. Your second foot catches the ball at the end of the spin.',
      },
      {
        id: 'trk-10',
        title: 'Double Touch',
        description: 'While dribbling, flick the ball forward with your laces, then immediately redirect it with the outside of the same foot. 5 times.',
        difficulty: 3,
        tip: 'The first touch sets up the second touch. The two touches happen close together — quick-quick, then go!',
      },
      {
        id: 'trk-11',
        title: 'No-Look Heel Pass',
        description: 'Stand with your back to a target. Without looking, pass the ball accurately to it using your heel. 3 out of 5.',
        difficulty: 3,
        tip: 'Feel where the target is before you start. Flick through the center of the ball with your heel snap.',
      },
      {
        id: 'trk-12',
        title: 'Freestyle Combo',
        description: 'Put together 3 different skills in a row: a trick, a dribble, and a shot. Nail the full combo 3 times.',
        difficulty: 3,
        tip: 'Practice each part separately first, then chain them. Your combo — your style!',
      },
    ],
  },
}

export const TRACK_IDS: TrackId[] = ['juggling', 'dribbling', 'passing', 'shooting', 'control', 'tricks']

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

export function getUnlockedChallengeIds(track: Track, completedIds: Set<string>): Set<string> {
  const byDiff: Record<number, Challenge[]> = { 1: [], 2: [], 3: [] }
  for (const c of track.challenges) byDiff[c.difficulty].push(c)

  const unlocked = new Set<string>()
  byDiff[1].forEach((c) => unlocked.add(c.id))

  if (byDiff[1].every((c) => completedIds.has(c.id))) {
    byDiff[2].forEach((c) => unlocked.add(c.id))
  }

  if (byDiff[2].every((c) => completedIds.has(c.id))) {
    byDiff[3].forEach((c) => unlocked.add(c.id))
  }

  return unlocked
}
