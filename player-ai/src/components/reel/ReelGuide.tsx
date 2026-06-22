'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface ReelGuideProps {
  defaultTabIndex: number;
  playerPosition: string;
}

const TABS = [
  'Goalkeeper',
  'Center Back',
  'Full Back',
  'Midfielder',
  'Winger',
  'Striker',
];

const POSITION_CONTENT = [
  // Index 0 — Goalkeeper
  {
    priorities: [
      {
        title: 'Distribution quality',
        text: 'Goal kicks, throws, played passes under pressure. Modern coaches care more about this than almost anything else. Show clips of you playing out under a press, not just saves.',
      },
      {
        title: 'Shot stopping',
        text: '2–3 clips of different save types — near post driven shot, diving save, reaction save. Do not show 8 saves. Show 3 exceptional ones.',
      },
      {
        title: 'Cross claiming',
        text: 'One or two clips of you commanding and catching a cross confidently, especially in traffic.',
      },
      {
        title: '1v1 situations',
        text: 'One clip of you saving a 1v1 cleanly, staying big and forcing the shot into your body.',
      },
    ],
    leaveOut: 'Punching crosses (shows uncertainty), routine catches, any save where the shot was weak, long goal kicks where you cannot see the outcome.',
    structure: 'Open with your best save (10s). Distribution sequence showing 2–3 clean plays out of the back (30s). Cross claiming clip (15s). Second strong save (10s). 1v1 clip (10s). Close with a confident distribution moment (10s). Total: ~85 seconds.',
  },
  // Index 1 — Center Back
  {
    priorities: [
      {
        title: 'Composure on the ball',
        text: 'Clips of you receiving under pressure and playing out cleanly. This is what separates modern CBs. Show at least 2 clips.',
      },
      {
        title: 'Aerial duels',
        text: 'One or two clips of you winning a header decisively, both defensive and attacking set pieces if possible.',
      },
      {
        title: '1v1 defending',
        text: 'One clip of you staying disciplined, showing a striker inside, and winning the ball cleanly.',
      },
      {
        title: 'Reading the game',
        text: 'A clip of you stepping to intercept a through ball or cutting off a passing lane. Hard to film but extremely valuable.',
      },
    ],
    leaveOut: 'Slide tackles (show last resort, not first option), clearances that go nowhere, headers that lack conviction.',
    structure: 'Composure under press clip (15s). Aerial duel won (10s). 1v1 defense clip (15s). Distribution sequence showing range of passing (20s). Set piece defensive moment (10s). Best individual defending moment (15s). Total: ~85 seconds.',
  },
  // Index 2 — Full Back
  {
    priorities: [
      {
        title: 'Defending wide',
        text: 'Your ability to handle a winger 1v1 without diving in. One clip of you staying disciplined and winning.',
      },
      {
        title: 'Attacking contribution',
        text: 'An overlap run that leads to a cross or combination. Shows coaches you understand the modern FB role.',
      },
      {
        title: 'Recovery pace',
        text: 'A clip of you tracking back after getting caught high. Shows work ethic and recovery speed.',
      },
      {
        title: 'Crossing quality',
        text: 'If you have a quality cross that leads to a chance or goal, include it. If not, do not force it.',
      },
    ],
    leaveOut: 'Overlapping runs that end without a cross or combination, tracking back runs where you are clearly beaten, any defensive moment where you dive in and get turned.',
    structure: 'Best defending 1v1 clip (15s). Overlap into crossing position (15s). Recovery run clip (10s). Second defending clip (10s). Combination with winger (15s). Total: ~65 seconds.',
  },
  // Index 3 — Midfielder
  {
    priorities: [
      {
        title: 'Receiving and turning under pressure',
        text: 'The single most important technical skill for midfielders in the college game. Show at least 2 clips of you receiving and playing forward quickly.',
      },
      {
        title: 'Progressive passing',
        text: 'A clip of a through ball or line-breaking pass that creates a chance. Shows vision.',
      },
      {
        title: 'Pressing and winning the ball',
        text: 'One clip of you winning the ball in the middle third and transitioning immediately.',
      },
      {
        title: 'Box arrivals',
        text: 'If you have a goal or assist from a run from deep, include it. This separates midfielders at the next level.',
      },
    ],
    leaveOut: 'Sideways passes, square balls, any moment where you played safe when forward was available.',
    structure: 'Best receiving-and-turning sequence (20s). Progressive pass leading to a chance (10s). Ball won and quick transition (15s). Box arrival or goal (15s). Second receiving sequence showing range (15s). Total: ~75 seconds.',
  },
  // Index 4 — Winger
  {
    priorities: [
      {
        title: '1v1 in wide areas',
        text: 'The ability to beat a defender and create a crossing or shooting opportunity. Baseline expectation at college level. Show 2–3 clips.',
      },
      {
        title: 'Goals and assists',
        text: 'If you have them, they go first. College coaches recruit output.',
      },
      {
        title: 'Pressing from the front',
        text: 'One clip of you forcing a turnover or cutting off a goal kick with your pressing angle.',
      },
      {
        title: 'Weak foot involvement',
        text: 'If you can cut inside onto your weak foot and shoot, film it. Left-footed finishes by a right-footed winger are memorable.',
      },
    ],
    leaveOut: 'Any cross that does not find a teammate, runs in behind that come to nothing, clips where you beat a defender but then lose the ball.',
    structure: 'Best goal or assist (10s). First 1v1 won into cross or shot (15s). Second 1v1 sequence (15s). Pressing clip (10s). Weak foot moment if you have it (10s). Final highlight (15s). Total: ~75 seconds.',
  },
  // Index 5 — Striker
  {
    priorities: [
      {
        title: 'Finishing',
        text: 'Goals of different types — near post, far post, header, weak foot. Variety shows technical range.',
      },
      {
        title: 'Movement',
        text: 'A clip showing your off-ball movement creating space for a teammate even when you do not score. Demonstrates tactical intelligence.',
      },
      {
        title: 'Hold-up play',
        text: 'One clip of you receiving with your back to goal, holding a defender off, and playing a teammate in.',
      },
      {
        title: 'Pressing from the front',
        text: 'College coaches want strikers who work. Show one clip of your pressing effort leading to a turnover or forcing a mistake.',
      },
    ],
    leaveOut: 'Missed chances, any clip where the goalkeeper saves a weak shot, goals where the goalkeeper is not between the posts.',
    structure: 'Best goal (10s). Second goal showing different finish type (10s). Movement clip — space created (15s). Hold-up play and assist (15s). Pressing clip (10s). Third goal or best attacking moment (10s). Total: ~70 seconds.',
  },
];

const TIMELINE_ROWS = [
  { grade: '8th Grade',  target: 'End of 8th grade year',        status: 'Training clips only OK',   action: 'Attend showcases, get filmed' },
  { grade: '9th Grade',  target: 'Start of sophomore year',       status: 'First game reel ready',     action: 'Submit to ID camps, build list' },
  { grade: '10th Grade', target: 'Summer before junior year',     status: 'Full polished reel',        action: 'Email coaches, register NCSA' },
  { grade: '11th Grade', target: 'Fall of junior year',           status: 'Final reel locked',         action: 'Official visits, verbal commits' },
  { grade: '12th Grade', target: 'First month of school',         status: 'Signing reel ready',        action: 'NLI signing if committing' },
];

export default function ReelGuide({ defaultTabIndex, playerPosition }: ReelGuideProps) {
  const [activeTab, setActiveTab] = useState(defaultTabIndex);
  const content = POSITION_CONTENT[activeTab] ?? POSITION_CONTENT[0];

  return (
    <div className="space-y-10">

      {/* Section 1 — 4 Universal Rules */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">4 Rules Every Reel Must Follow</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Coaches watch hundreds of reels a week. Get these right before worrying about anything else.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            {
              number: '1',
              title: 'Keep it under 3 minutes',
              text: 'A 6-minute reel signals the player and family do not understand the recruiting process. 90 seconds to 3 minutes is the sweet spot.',
            },
            {
              number: '2',
              title: 'Quality over quantity',
              text: 'Eight clips of you doing something exceptional beat twenty clips of average plays. Every clip should make the coach think "I want to see more."',
            },
            {
              number: '3',
              title: 'Real game footage only',
              text: 'Training clips can supplement but should never lead. Coaches want to see how you perform under real match pressure, with real opponents.',
            },
            {
              number: '4',
              title: 'Start strong',
              text: 'The first 20 seconds determine whether a coach watches the rest. Lead with your single best moment. Do not build up to it.',
            },
          ].map((rule) => (
            <Card key={rule.number} className="border-border/50 bg-card/40">
              <CardContent className="p-5 space-y-2">
                <div className="text-3xl font-black text-primary">{rule.number}</div>
                <div className="text-sm font-bold text-white">{rule.title}</div>
                <div className="text-xs text-muted-foreground leading-relaxed">{rule.text}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Section 2 — Position-Specific Tabs */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Position-Specific Requirements</h2>
          {playerPosition && (
            <p className="text-sm text-muted-foreground mt-1">
              Showing guide for your position: <span className="text-primary font-semibold">{playerPosition}</span>. Select a tab to explore others.
            </p>
          )}
        </div>

        {/* Tab bar */}
        <div className="flex flex-wrap gap-2">
          {TABS.map((tab, i) => (
            <button
              key={i}
              onClick={() => setActiveTab(i)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-150 border ${
                activeTab === i
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="space-y-4">
          {/* Priorities */}
          <Card className="border-border/50 bg-card/40">
            <CardContent className="p-5 space-y-3">
              <p className="text-xs font-bold text-primary uppercase tracking-widest">
                What Coaches Prioritize
              </p>
              <ol className="space-y-3">
                {content.priorities.map((p, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="text-primary font-black text-sm shrink-0 mt-0.5">{i + 1}.</span>
                    <div>
                      <span className="text-sm font-bold text-white">{p.title}: </span>
                      <span className="text-sm text-muted-foreground">{p.text}</span>
                    </div>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Leave out */}
            <Card className="border-destructive/20 bg-destructive/5">
              <CardContent className="p-5 space-y-2">
                <p className="text-xs font-bold text-destructive uppercase tracking-widest">
                  What to Leave Out
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {content.leaveOut}
                </p>
              </CardContent>
            </Card>

            {/* Ideal structure */}
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="p-5 space-y-2">
                <p className="text-xs font-bold text-primary uppercase tracking-widest">
                  Ideal Reel Structure
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {content.structure}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Section 3 — Recruiting Timeline */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Recruiting Timeline</h2>
          <p className="text-sm text-muted-foreground mt-1">
            When to have your reel ready throughout your high school career.
          </p>
        </div>
        <Card className="border-border/50 bg-card/40 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/50 bg-secondary/30">
                  <th className="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wider">Grade</th>
                  <th className="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wider">Target Date</th>
                  <th className="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wider">Reel Status</th>
                  <th className="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wider">Priority Action</th>
                </tr>
              </thead>
              <tbody>
                {TIMELINE_ROWS.map((row, i) => (
                  <tr key={i} className="border-b border-border/30 last:border-0 hover:bg-secondary/20 transition-colors">
                    <td className="px-4 py-3 font-semibold text-white">{row.grade}</td>
                    <td className="px-4 py-3 text-muted-foreground">{row.target}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{row.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Section 4 — Athlete2Athlete teaser */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 space-y-2">
        <h3 className="text-lg font-bold text-white">
          Athlete2Athlete — Coming Soon
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
          Soon you will be able to submit your game footage directly to Mitch, Nick, or Liam for a personal video review — and book a live 30-minute Q&A session with a current college or professional player who plays your position.
        </p>
        <p className="text-xs text-muted-foreground/60 pt-1">
          Reel Reviews · Live Q&A · Position-Specific Mentorship
        </p>
      </div>

    </div>
  );
}
