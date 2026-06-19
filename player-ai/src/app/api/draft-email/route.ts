import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/session';
import { checkRateLimit } from '@/lib/rate-limit';
import { getUserData } from '@/lib/data/getUserData';
import type { AthleteProfile } from '@/lib/types/player';

// 5 drafts per 10 minutes per user
const RATE_LIMIT = { limit: 5, windowMs: 10 * 60 * 1000 };

export async function POST(req: NextRequest) {
  // Auth — proxy enforces this too, but a direct check here makes the route
  // self-contained and gives a clean JSON error rather than a redirect.
  const username = await getCurrentUser();
  if (!username) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Rate limit per user
  const allowed = checkRateLimit(`draft-email:${username}`, RATE_LIMIT);
  if (!allowed) {
    return NextResponse.json(
      { error: 'Too many requests. Please wait a few minutes before drafting another email.' },
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
      gradYear,
      programInterest,
      tone,
    } = body;

    // Validate required string fields from client
    if (!coachLastName || !schoolName || !gradYear) {
      return NextResponse.json({ error: 'Missing required fields.' }, { status: 400 });
    }

    // Fetch profile server-side — never trust client-supplied profile data
    const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');
    if (!profile) {
      return NextResponse.json({ error: 'Profile not found.' }, { status: 404 });
    }

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
    const instructions = toneInstructions[tone as string] ?? '';

    const systemPrompt = `You are a college soccer recruiting email writer. You write authentic, effective recruiting emails on behalf of high school soccer players reaching out to college coaches.

CRITICAL RULES:
- The email must sound like a real high school athlete wrote it — NOT like AI
- Never use these clichés: "I have always dreamed", "I believe I would be a great fit", "passionate about", "I would be honored", "reaching out to express my interest"
- Keep the body under 200 words — college coaches get hundreds of emails
- Be specific — use the coach's name, school name, and conference
- End with ONE clear, specific ask (a call, ID camp info, or film review)
- Include academics naturally only if GPA ≥ 3.5 or test scores are provided
- Do NOT mention Player AI or any platform by name
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

Target Coach: Coach ${coachLastName} (${coachFirstName} ${coachLastName})
School: ${schoolName}
Conference: ${conference}
Region: ${region}

What the player wants to mention specifically: ${programInterest || 'nothing specific provided — write a strong general interest email'}

Subject line format: [Position] Prospect | [Player Name] | Class of [Year] | [School Name]`;

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey || apiKey === 'mock-key' || apiKey.startsWith('your_') || apiKey.trim() === '') {
      console.warn('ANTHROPIC_API_KEY not configured — returning mock draft.');
      return NextResponse.json(buildMockDraft(profile, coachLastName, schoolName, conference, gradYear, programInterest));
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
    console.error('draft-email error:', err);
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
