import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/session';
import { checkRateLimit } from '@/lib/rate-limit';
import { log } from '@/lib/logger';
import { getUserData } from '@/lib/data/getUserData';
import type { AthleteProfile } from '@/lib/types/player';

// 5 drafts per 10 minutes per user (burst)
const RATE_LIMIT_BURST = { limit: 5,  windowMs: 10 * 60 * 1000 };
// 20 drafts per day per user (cost cap)
const RATE_LIMIT_DAILY = { limit: 20, windowMs: 24 * 60 * 60 * 1000 };

export async function POST(req: NextRequest) {
  // Auth — proxy enforces this too, but a direct check here makes the route
  // self-contained and gives a clean JSON error rather than a redirect.
  const username = await getCurrentUser();
  if (!username) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Rate limit per user — burst then daily cap
  if (!checkRateLimit(`draft-email:burst:${username}`, RATE_LIMIT_BURST)) {
    log.aiRateLimited(username);
    return NextResponse.json(
      { error: 'Too many requests. Please wait a few minutes before drafting another email.' },
      { status: 429 }
    );
  }
  if (!checkRateLimit(`draft-email:daily:${username}`, RATE_LIMIT_DAILY)) {
    log.aiRateLimited(username);
    return NextResponse.json(
      { error: 'Daily email draft limit reached (20 per day). Come back tomorrow.' },
      { status: 429 }
    );
  }

  try {
    const body = await req.json();
    const {
      coachFirstName,
      coachLastName,
      schoolName,
      conference,
      region,
      programInterest,
      tone,
    } = body;

    // Validate required fields
    if (!coachLastName || !schoolName) {
      return NextResponse.json({ error: 'Missing required fields.' }, { status: 400 });
    }

    // Strict type + length validation on every client-supplied string
    const VALID_TONES = ['formal', 'balanced', 'direct'] as const;
    type Tone = typeof VALID_TONES[number];

    function sanitizeString(val: unknown, name: string, maxLen: number): string {
      if (val !== undefined && val !== null && typeof val !== 'string') {
        throw Object.assign(new Error(`${name} must be a string`), { status: 400 });
      }
      const s = (val as string | undefined | null)?.trim() ?? '';
      if (s.length > maxLen) {
        throw Object.assign(new Error(`${name} exceeds maximum length of ${maxLen}`), { status: 400 });
      }
      return s;
    }

    let safeFirstName: string, safeLastName: string, safeSchool: string,
        safeConference: string, safeRegion: string, safeInterest: string;

    try {
      safeFirstName  = sanitizeString(coachFirstName,  'coachFirstName',  100);
      safeLastName   = sanitizeString(coachLastName,   'coachLastName',   100);
      safeSchool     = sanitizeString(schoolName,      'schoolName',      150);
      safeConference = sanitizeString(conference,      'conference',      100);
      safeRegion     = sanitizeString(region,          'region',          100);
      safeInterest   = sanitizeString(programInterest, 'programInterest', 2000);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Invalid input.';
      return NextResponse.json({ error: msg }, { status: 400 });
    }

    if (tone !== undefined && !VALID_TONES.includes(tone as Tone)) {
      return NextResponse.json({ error: 'Invalid tone value.' }, { status: 400 });
    }
    const safeTone: Tone = VALID_TONES.includes(tone as Tone) ? (tone as Tone) : 'balanced';

    // Fetch profile server-side — never trust client-supplied profile data
    const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');
    if (!profile) {
      return NextResponse.json({ error: 'Profile not found.' }, { status: 404 });
    }

    // Use grad_year from profile (DB); fall back to client-supplied only as last resort
    const gradYear = String(profile.grad_year ?? body.gradYear ?? new Date().getFullYear() + 3);

    // Build academic context string
    const academicLines: string[] = [];
    if (profile.gpa) {
      academicLines.push(`GPA: ${profile.gpa}${profile.gpa_scale ? ` (${profile.gpa_scale} scale)` : ''}`);
    }
    if (profile.act_score) academicLines.push(`ACT: ${profile.act_score}`);
    if (profile.sat_score) academicLines.push(`SAT: ${profile.sat_score}`);
    const academicContext = academicLines.length > 0
      ? `Academic profile: ${academicLines.join(', ')}.`
      : 'No academic scores provided.';

    // Tone instructions
    const toneInstructions: Record<string, string> = {
      formal: 'Write in a formal, measured tone. Lead with character and academics before athletics. Use structured language. The player sounds mature and serious about their education.',
      balanced: 'Write in a balanced, professional-but-warm tone. Equal weight on athletics and academics. Conversational but respectful.',
      direct: 'Write in a confident, direct tone. Lead immediately with athletic credentials. Short punchy sentences. The player sounds competitive and driven.',
    };
    const instructions = toneInstructions[safeTone];

    const systemPrompt = `You are a college soccer recruiting email writer. You write authentic, effective recruiting emails on behalf of high school soccer players reaching out to college coaches.

CRITICAL RULES:
- The email must sound like a real high school athlete wrote it — NOT like AI
- Never use these clichés: "I have always dreamed", "I believe I would be a great fit", "passionate about", "I would be honored", "reaching out to express my interest"
- Keep the body under 200 words — college coaches get hundreds of emails
- Be specific — use the coach's name, school name, and conference
- End with ONE clear, specific ask (a call, ID camp info, or film review)
- Include academics naturally only if GPA ≥ 3.5 or test scores are provided
- Do NOT mention Footy Mentor or any platform by name
- NEVER use placeholder brackets like [Club Name], [High School Name], [Phone Number], [Email Address] — if data is missing, omit that detail entirely rather than leaving a bracket placeholder
- Output ONLY valid JSON — no preamble, no markdown fences

${instructions}

Output format (JSON only):
{
  "subject": "subject line here",
  "body": "full email body here with \\n for line breaks"
}`;

    const userPrompt = `Write a recruiting email with these details:

Player: ${profile.name}
Position: ${profile.position}
Level: ${profile.level}
Graduation Year: ${gradYear}
Focus Areas: ${profile.focus_areas?.join(', ') ?? 'not specified'}
${academicContext}

Target Coach: Coach ${safeLastName} (${safeFirstName} ${safeLastName})
School: ${safeSchool}
Conference: ${safeConference}
Region: ${safeRegion}

What the player wants to mention specifically: ${safeInterest || 'nothing specific provided — write a strong general interest email'}

Subject line format: [Position] Prospect | [Player Name] | Class of [Year] | [Target School Name]
Note: [Target School Name] must be exactly "${safeSchool}" — the university the player is writing TO, not their current school.`;

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey || apiKey === 'mock-key' || apiKey.startsWith('your_') || apiKey.trim() === '') {
      console.warn('ANTHROPIC_API_KEY not configured — returning mock draft.');
      return NextResponse.json(buildMockDraft(profile, safeLastName, safeSchool, safeConference, gradYear, safeInterest));
    }

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        messages: [{ role: 'user', content: userPrompt }],
        system: systemPrompt,
      }),
    });

    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.status}`);
    }

    const data = await response.json();
    const text = data.content?.[0]?.text ?? '';
    const clean = text.replace(/```json|```/g, '').trim();
    const parsed = JSON.parse(clean);

    return NextResponse.json({ subject: parsed.subject, body: parsed.body });
  } catch (err) {
    log.apiError('POST /api/draft-email', err);
    return NextResponse.json(
      { error: 'Failed to generate email. Please try again.' },
      { status: 500 }
    );
  }
}

function buildMockDraft(
  profile: { name: string; position: string; level: string; gpa?: number; gpa_scale?: string; sat_score?: number; act_score?: number; focus_areas?: string[] },
  coachLastName: string,
  schoolName: string,
  conference: string,
  gradYear: string,
  programInterest?: string,
) {
  const subject = `${profile.position} Prospect | ${profile.name} | Class of ${gradYear} | ${schoolName}`;

  const academicText = profile.gpa
    ? `Academically, I carry a ${profile.gpa} GPA${profile.gpa_scale ? ` (${profile.gpa_scale} scale)` : ''}.${profile.sat_score || profile.act_score ? ` Test scores: ${[profile.sat_score ? `SAT ${profile.sat_score}` : '', profile.act_score ? `ACT ${profile.act_score}` : ''].filter(Boolean).join(', ')}.` : ''}`
    : '';

  const body = `Coach ${coachLastName},

My name is ${profile.name}, a ${profile.level} ${profile.position} in the Class of ${gradYear}. I'm interested in the ${schoolName} program.

${programInterest || `I've been following ${schoolName} in the ${conference} and like what I see from your program.`}

${academicText}
My training focus is ${profile.focus_areas?.slice(0, 2).join(' and ') ?? 'technical development'}. Would love to connect about upcoming ID camps or share film.

${profile.name}
${profile.position} · Class of ${gradYear}`;

  return { subject, body };
}
