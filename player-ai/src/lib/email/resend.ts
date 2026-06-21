import { Resend } from 'resend';
import type { AthleteProfile, WeeklyTrainingPlan, RRSHistory } from '@/lib/types/player';
import { calculateRRS } from '@/lib/utils/calculateRRS';
import { calculateSkillRadar } from '@/lib/utils/calculateSkillRadar';
import type { CompletionLog, Drill } from '@/lib/types/player';

const resend = new Resend(process.env.RESEND_API_KEY);
const APP_URL = process.env.RESEND_APP_URL || 'http://localhost:3000';
// For production: verify a custom domain at resend.com/domains and set RESEND_FROM_EMAIL=Player AI <noreply@yourdomain.com>
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'Player AI <onboarding@resend.dev>';

export async function sendPasswordResetEmail(params: {
  email: string;
  username: string;
  token: string;
}): Promise<void> {
  const { email, username, token } = params;
  const resetUrl = `${APP_URL}/reset-password?token=${token}`;

  await resend.emails.send({
    from: FROM_EMAIL,
    to: email,
    subject: 'Reset your Player AI password',
    html: `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117;padding:32px 16px;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;">
        <tr><td style="text-align:center;padding-bottom:24px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:0.15em;color:#6b7280;text-transform:uppercase;">Player AI</div>
        </td></tr>
        <tr><td style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:32px 28px;">
          <div style="font-size:22px;font-weight:800;color:#ffffff;margin-bottom:8px;">Reset your password</div>
          <div style="font-size:14px;color:#9ca3af;margin-bottom:24px;">
            Hi <strong style="color:#e5e7eb;">${username}</strong>, we received a request to reset your password.
            Click the button below — this link expires in <strong style="color:#e5e7eb;">1 hour</strong>.
          </div>
          <div style="text-align:center;margin-bottom:24px;">
            <a href="${resetUrl}"
               style="display:inline-block;background:#22c55e;color:#000000;font-weight:700;font-size:14px;padding:12px 32px;border-radius:8px;text-decoration:none;">
              Reset Password →
            </a>
          </div>
          <div style="font-size:12px;color:#6b7280;border-top:1px solid #2d3748;padding-top:16px;">
            If you didn't request this, you can safely ignore this email — your password won't change.
            <br><br>
            Or copy this link into your browser:<br>
            <span style="color:#9ca3af;word-break:break-all;">${resetUrl}</span>
          </div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`,
  });
}

export async function sendWeeklySummaryEmail(params: {
  profile: AthleteProfile;
  completionLog: CompletionLog;
  plan: WeeklyTrainingPlan;
  drills: Drill[];
  rrsHistory: RRSHistory | null;
  completedWeekNumber: number;
}): Promise<void> {
  const { profile, completionLog, plan, drills, rrsHistory, completedWeekNumber } = params;

  if (!profile.email) return;

  // Calculate RRS
  const rrs = calculateRRS(profile, completionLog, plan, drills, rrsHistory);

  if (!rrs.unlocked) {
    return;
  }

  // Calculate skill radar — find top skill
  const radar = calculateSkillRadar(profile, completionLog, plan, drills);
  let topSkill = 'Keep training to unlock skill data';
  if (radar.hasData && radar.axes.length > 0) {
    const topIndex = radar.scores.indexOf(Math.max(...radar.scores));
    topSkill = radar.axes[topIndex] ?? topSkill;
  }

  // Sessions completed vs planned for the completed week
  const completedWeek = plan.weeks?.find(w => w.week_number === completedWeekNumber);
  const sessionsPlanned = completedWeek?.sessions?.length ?? 0;
  const sessionsCompleted = completedWeek?.sessions?.filter(s => s.completed).length ?? 0;

  // Drills completed this week
  const completionsThisWeek = completionLog.completions.filter(c => c.week === completedWeekNumber);
  const drillsThisWeek = completionsThisWeek.reduce(
    (sum, c) => sum + (c.drills_completed?.length ?? 0), 0
  );

  // Next week session names
  const nextWeekNumber = completedWeekNumber + 1;
  const nextWeek = plan.weeks?.find(w => w.week_number === nextWeekNumber);
  const nextSessionNames = nextWeek?.sessions?.map(s => s.name) ?? [];

  // Delta label
  const deltaStr = rrs.weeklyDelta >= 0
    ? `+${rrs.weeklyDelta}`
    : `${rrs.weeklyDelta}`;

  const html = buildEmailHtml({
    name: profile.name,
    weekNumber: completedWeekNumber,
    rrsScore: rrs.overall,
    deltaStr,
    benchmarkLabel: rrs.benchmark.label,
    sessionsCompleted,
    sessionsPlanned,
    drillsThisWeek,
    topSkill,
    nextSessionNames,
    nextActions: rrs.nextActions.slice(0, 2),
    appUrl: APP_URL,
  });

  await resend.emails.send({
    from: FROM_EMAIL,
    to: profile.email,
    subject: `Week ${completedWeekNumber} Complete — Your Player AI Summary`,
    html,
  });
}

function buildEmailHtml(data: {
  name: string;
  weekNumber: number;
  rrsScore: number;
  deltaStr: string;
  benchmarkLabel: string;
  sessionsCompleted: number;
  sessionsPlanned: number;
  drillsThisWeek: number;
  topSkill: string;
  nextSessionNames: string[];
  nextActions: string[];
  appUrl: string;
}): string {
  const {
    name, weekNumber, rrsScore, deltaStr, benchmarkLabel,
    sessionsCompleted, sessionsPlanned, drillsThisWeek,
    topSkill, nextSessionNames, nextActions, appUrl,
  } = data;

  const nextWeekNumber = weekNumber + 1;

  const nextSessionsHtml = nextSessionNames.length > 0
    ? nextSessionNames.map(n => `<li style="margin:4px 0;color:#d1d5db;">${n}</li>`).join('')
    : '<li style="color:#6b7280;">No sessions generated yet</li>';

  const nextActionsHtml = nextActions.length > 0
    ? nextActions.map(a => `<li style="margin:6px 0;color:#d1d5db;">${a}</li>`).join('')
    : '<li style="color:#6b7280;">Keep training to unlock recommendations</li>';

  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117;padding:32px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <!-- Header -->
        <tr><td style="text-align:center;padding-bottom:28px;">
          <div style="font-size:28px;margin-bottom:6px;">⚽</div>
          <div style="font-size:11px;font-weight:700;letter-spacing:0.15em;color:#6b7280;text-transform:uppercase;">Player AI</div>
        </td></tr>

        <!-- Hero -->
        <tr><td style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:28px 24px;text-align:center;margin-bottom:16px;">
          <div style="font-size:13px;color:#6b7280;margin-bottom:4px;">Week ${weekNumber} Complete</div>
          <div style="font-size:26px;font-weight:800;color:#ffffff;margin-bottom:2px;">Nice work, ${name}.</div>
          <div style="font-size:13px;color:#9ca3af;">Here's how your week looked.</div>
        </td></tr>

        <tr><td style="height:12px;"></td></tr>

        <!-- RRS Score -->
        <tr><td style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:24px;text-align:center;">
          <div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#6b7280;text-transform:uppercase;margin-bottom:8px;">Readiness & Retention Score</div>
          <div style="font-size:52px;font-weight:900;color:#22c55e;line-height:1;">${rrsScore}</div>
          <div style="font-size:14px;color:#9ca3af;margin-top:4px;">${deltaStr} this week &nbsp;·&nbsp; ${benchmarkLabel}</div>
        </td></tr>

        <tr><td style="height:12px;"></td></tr>

        <!-- Stats Row -->
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td width="32%" style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:16px;text-align:center;">
                <div style="font-size:26px;font-weight:800;color:#ffffff;">${sessionsCompleted}/${sessionsPlanned}</div>
                <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Sessions</div>
              </td>
              <td width="4%"></td>
              <td width="32%" style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:16px;text-align:center;">
                <div style="font-size:26px;font-weight:800;color:#ffffff;">${drillsThisWeek}</div>
                <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Drills Done</div>
              </td>
              <td width="4%"></td>
              <td width="32%" style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:16px;text-align:center;">
                <div style="font-size:15px;font-weight:800;color:#22c55e;line-height:1.2;">${topSkill}</div>
                <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Top Skill</div>
              </td>
            </tr>
          </table>
        </td></tr>

        <tr><td style="height:12px;"></td></tr>

        <!-- Next Week -->
        <tr><td style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:20px 24px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#6b7280;text-transform:uppercase;margin-bottom:12px;">Week ${nextWeekNumber} Sessions</div>
          <ul style="margin:0;padding:0 0 0 18px;">${nextSessionsHtml}</ul>
        </td></tr>

        <tr><td style="height:12px;"></td></tr>

        <!-- Next Actions -->
        <tr><td style="background:#1a1f2e;border:1px solid #2d3748;border-radius:12px;padding:20px 24px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#6b7280;text-transform:uppercase;margin-bottom:12px;">Next Actions</div>
          <ul style="margin:0;padding:0 0 0 18px;">${nextActionsHtml}</ul>
        </td></tr>

        <tr><td style="height:20px;"></td></tr>

        <!-- CTA -->
        <tr><td style="text-align:center;">
          <a href="${appUrl}" style="display:inline-block;background:#22c55e;color:#000000;font-weight:700;font-size:14px;padding:12px 32px;border-radius:8px;text-decoration:none;letter-spacing:0.02em;">
            Open Player AI →
          </a>
        </td></tr>

        <tr><td style="height:24px;"></td></tr>

        <!-- Footer -->
        <tr><td style="text-align:center;">
          <div style="font-size:11px;color:#4b5563;">You're receiving this because you have a Player AI account.</div>
          <div style="font-size:11px;color:#4b5563;margin-top:4px;">Update your email in <a href="${appUrl}/profile" style="color:#6b7280;">Profile Settings</a>.</div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>`;
}
