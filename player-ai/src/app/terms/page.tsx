import Link from 'next/link';

export const metadata = {
  title: 'Terms of Service — Player AI',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background px-4 py-12">
      <div className="max-w-3xl mx-auto space-y-10">

        {/* Header */}
        <div className="space-y-2">
          <Link href="/login" className="text-xs text-muted-foreground hover:text-primary transition-colors">
            ← Back to Sign In
          </Link>
          <h1 className="text-3xl font-black text-white tracking-tight mt-4">Terms of Service</h1>
          <p className="text-sm text-muted-foreground">
            Last updated: June 21, 2026 &nbsp;·&nbsp; Effective: June 21, 2026
          </p>
        </div>

        <div className="prose prose-invert prose-sm max-w-none space-y-8 text-muted-foreground leading-relaxed">

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">1. Who We Are</h2>
            <p>
              Player AI (&ldquo;Player AI,&rdquo; &ldquo;we,&rdquo; &ldquo;us,&rdquo; or &ldquo;our&rdquo;) is a soccer
              athlete development platform that provides personalized training plans, skill tracking, highlight reel
              submission and review, and tools to support the college recruiting process. These Terms of Service
              (&ldquo;Terms&rdquo;) govern your use of the Player AI website and application (the &ldquo;Service&rdquo;).
            </p>
            <p>
              By creating an account or using the Service, you agree to these Terms. If you do not agree,
              do not use the Service.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">2. Eligibility</h2>
            <p>
              You must be at least <strong className="text-foreground">13 years old</strong> to use Player AI.
              If you are between 13 and 17, a parent or legal guardian must review and agree to these Terms
              on your behalf, and they are responsible for your use of the Service.
            </p>
            <p>
              We do not knowingly collect personal information from children under 13. If we learn that a user
              is under 13, we will delete their account and all associated data promptly.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">3. Your Account</h2>
            <p>
              You are responsible for keeping your password confidential and for all activity that occurs
              under your account. You agree to:
            </p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>Provide accurate information when creating your profile</li>
              <li>Notify us immediately if you suspect unauthorized use of your account</li>
              <li>Not share your login credentials with others</li>
              <li>Not create accounts on behalf of other people without their authorization</li>
            </ul>
            <p>
              We reserve the right to suspend or terminate accounts that violate these Terms.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">4. What Player AI Does</h2>
            <p>The Service provides:</p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>
                <strong className="text-foreground">Training Plans:</strong> Personalized weekly session plans
                generated based on your profile, position, and goals
              </li>
              <li>
                <strong className="text-foreground">Progress Tracking:</strong> A Readiness &amp; Reliability Score
                (RRS) calculated from your logged training activity across four pillars: consistency, volume,
                coverage, and progression
              </li>
              <li>
                <strong className="text-foreground">Drill Library:</strong> A curated library of soccer drills
                matched to your skill level and available equipment
              </li>
              <li>
                <strong className="text-foreground">Highlight Reel Review:</strong> The ability to upload video
                clips (up to 50 MB each) and submit them for feedback from our coaching staff
              </li>
              <li>
                <strong className="text-foreground">AI-Assisted Recruiting Emails:</strong> Draft recruiting emails
                to college coaches, generated using an AI model. Your profile data is used to personalize
                each draft
              </li>
              <li>
                <strong className="text-foreground">Coach Finder:</strong> A database of NCAA Division I soccer
                coaches compiled from publicly available sources, used to identify recruiting targets
              </li>
              <li>
                <strong className="text-foreground">Mentor Feed:</strong> Curated advice and insights from
                professional and college athletes
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">5. AI-Generated Content</h2>
            <p>
              The recruiting email drafting feature uses an artificial intelligence model (Anthropic Claude)
              to generate text. When you use this feature, certain profile data — including your name,
              position, playing level, graduation year, and academic scores if provided — is sent to
              Anthropic&apos;s API to produce a draft.
            </p>
            <p>
              <strong className="text-foreground">Important:</strong> AI-generated drafts are starting points
              only. You are solely responsible for reviewing, editing, and sending any emails to coaches.
              Player AI makes no guarantee that any email will result in a recruiting inquiry, offer,
              scholarship, or any other outcome.
            </p>
            <p>
              The training plans, RRS scores, and drill recommendations generated by the Service are also
              produced algorithmically. They are not a substitute for advice from a qualified coach, trainer,
              or sports medicine professional.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">6. Your Content</h2>
            <p>
              You retain ownership of any video clips and other content you upload to the Service
              (&ldquo;Your Content&rdquo;). By uploading content, you grant Player AI a limited,
              non-exclusive license to store, display, and share Your Content with our coaching staff
              for the purpose of providing feedback to you.
            </p>
            <p>You agree not to upload content that:</p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>Depicts anyone under 13 without verified parental consent</li>
              <li>Is defamatory, harassing, or violates another person&apos;s privacy</li>
              <li>Infringes on third-party copyrights or trademarks</li>
              <li>Contains malware, scripts, or code intended to harm our systems</li>
            </ul>
            <p>
              We reserve the right to remove content that violates these Terms without notice.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">7. Coach and School Data</h2>
            <p>
              The Coach Finder feature displays contact information for NCAA Division I soccer coaches
              compiled from publicly available athletic department websites and directories. This data
              is provided for your personal recruiting use only.
            </p>
            <p>
              You agree to use coach contact information only to send genuine, individual recruiting
              communications. You may not use the data for bulk messaging, commercial purposes,
              or any purpose other than your personal college recruiting outreach.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">8. Prohibited Use</h2>
            <p>You agree not to:</p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>Attempt to reverse-engineer, scrape, or harvest data from the Service</li>
              <li>Use automated tools to access the Service at a rate that exceeds normal human usage</li>
              <li>Attempt to gain unauthorized access to other users&apos; accounts or data</li>
              <li>Use the Service to send unsolicited commercial messages or spam</li>
              <li>Misrepresent your identity, athletic credentials, or academic record</li>
              <li>Use the Service for any unlawful purpose</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">9. Paid Features (Future)</h2>
            <p>
              The Service is currently provided free of charge during our early-access period. We plan
              to introduce paid subscription tiers in the future, which may include features such as
              priority reel review, advanced analytics, and additional AI email drafts.
            </p>
            <p>
              We will provide at least 30 days&apos; notice before requiring payment for any feature
              currently available for free. Any payment terms will be governed by a separate agreement
              presented at the time of purchase.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">10. Disclaimers</h2>
            <p>
              THE SERVICE IS PROVIDED &ldquo;AS IS&rdquo; AND &ldquo;AS AVAILABLE&rdquo; WITHOUT WARRANTY
              OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED,
              ERROR-FREE, OR FREE OF VIRUSES OR OTHER HARMFUL COMPONENTS.
            </p>
            <p>
              Player AI does not guarantee any recruiting outcomes. The presence of a coach&apos;s
              contact information in the Coach Finder does not imply any relationship with, endorsement by,
              or interest from that coach or institution.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">11. Limitation of Liability</h2>
            <p>
              TO THE FULLEST EXTENT PERMITTED BY LAW, PLAYER AI AND ITS FOUNDERS, EMPLOYEES, AND
              CONTRACTORS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL,
              OR PUNITIVE DAMAGES ARISING OUT OF YOUR USE OF (OR INABILITY TO USE) THE SERVICE.
            </p>
            <p>
              OUR TOTAL LIABILITY TO YOU FOR ANY CLAIMS ARISING FROM YOUR USE OF THE SERVICE SHALL
              NOT EXCEED THE AMOUNT YOU PAID US IN THE 12 MONTHS PRECEDING THE CLAIM, OR $50,
              WHICHEVER IS GREATER.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">12. Changes to These Terms</h2>
            <p>
              We may update these Terms from time to time. We will notify you by updating the
              &ldquo;Last updated&rdquo; date above. If we make material changes, we will provide
              at least 14 days&apos; notice by email (if you have provided one) or by a prominent
              notice within the Service. Your continued use after notice constitutes acceptance
              of the updated Terms.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">13. Governing Law</h2>
            <p>
              These Terms are governed by the laws of the State of [YOUR STATE], without regard to
              its conflict-of-law provisions. Any disputes shall be resolved in the courts located
              in [YOUR COUNTY/STATE].
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-white">14. Contact</h2>
            <p>
              If you have questions about these Terms, please contact us at:
            </p>
            <p className="text-foreground font-medium">
              [YOUR CONTACT EMAIL]
            </p>
          </section>

        </div>

        {/* Footer links */}
        <div className="border-t border-border/30 pt-6 flex flex-wrap gap-4 text-xs text-muted-foreground">
          <Link href="/privacy" className="hover:text-primary transition-colors">Privacy Policy</Link>
          <Link href="/login" className="hover:text-primary transition-colors">Back to Sign In</Link>
        </div>

      </div>
    </div>
  );
}
