import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)
const FROM = 'How 2 Soccer <noreply@how2soccer.com>'
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL ?? 'http://localhost:3001'

export async function sendConsentEmail(email: string, token: string): Promise<void> {
  const link = `${BASE_URL}/api/confirm-consent?token=${encodeURIComponent(token)}`

  await resend.emails.send({
    from: FROM,
    to: email,
    subject: 'Confirm your How 2 Soccer account',
    html: `
      <p>Hi there!</p>
      <p>Click the button below to confirm your email and activate your How 2 Soccer parent account.</p>
      <p>
        <a href="${link}" style="display:inline-block;background:#22c55e;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">
          Confirm my account
        </a>
      </p>
      <p style="color:#6b7280;font-size:13px;">This link expires in 24 hours. If you didn't sign up, ignore this email.</p>
      <p style="color:#6b7280;font-size:13px;">Link: <a href="${link}">${link}</a></p>
    `,
  })
}
