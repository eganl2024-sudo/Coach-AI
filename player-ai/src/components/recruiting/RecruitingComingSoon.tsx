'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog } from '@/components/ui/dialog';
import Link from 'next/link';
import type { AthleteProfile } from '@/lib/types/player';
import type { ProgramWithCoaches, CoachRecord, OutreachLog } from '@/lib/types/recruiting';
import { cn } from '@/lib/utils';
import OutreachTracker from './OutreachTracker';

interface RecruitingComingSoonProps {
  profile: AthleteProfile | null;
  programs: ProgramWithCoaches[];
  outreachLog: OutreachLog;
}

const FEATURES = [
  {
    icon: '🔍',
    title: 'Coach Finder',
    description: 'Search 212 D1 programs by division, conference, and region. Find the right coaches and their direct contact information in seconds.',
    stat: '212 D1 Programs',
  },
  {
    icon: '✉️',
    title: 'AI Email Drafter',
    description: 'Generate personalized recruiting emails using your Player AI profile. Your position, level, highlight reel, and focus areas — pre-filled and ready to personalize.',
    stat: 'Coming Soon',
  },
  {
    icon: '📋',
    title: 'Outreach Tracker',
    description: 'Track every coach you have contacted, log their responses, and follow up systematically. Never lose track of where you stand with a program.',
    stat: 'Full Pipeline View',
  },
];

const REGIONS = ['All', 'Northeast', 'Southeast', 'Midwest', 'West', 'Southwest'];

function pluralizeTitle(title: string, count: number): string {
  if (title === 'Assistant Coach') return count > 1 ? 'Assistant Coaches' : 'Assistant Coach';
  if (title === 'Director of Operations') return count > 1 ? 'Directors of Operations' : 'Director of Operations';
  return title; // Head Coach stays as-is
}

export default function RecruitingComingSoon({ profile, programs, outreachLog }: RecruitingComingSoonProps) {
  const name = profile?.name ?? 'Athlete';
  const position = profile?.position ?? 'Goalkeeper';
  const level = profile?.level ?? 'Competitive Club';
  const gradYear = profile?.age ? new Date().getFullYear() + (18 - profile.age) : new Date().getFullYear() + 2;

  // Search & Filter State
  const [search, setSearch] = useState('');
  const [region, setRegion] = useState('All');
  const [conference, setConference] = useState('All');
  const [emailOnly, setEmailOnly] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState<ProgramWithCoaches | null>(null);

  // Outreach prefill state
  const [prefilledOutreach, setPrefilledOutreach] = useState<{
    school_name: string;
    coach_name: string;
    coach_title: string;
    coach_email: string | null;
  } | null>(null);

  // Email Drafter State
  type DraftStep = 'staff' | 'form' | 'draft';
  const [draftStep, setDraftStep] = useState<DraftStep>('staff');
  const [draftGradYear, setDraftGradYear] = useState(gradYear.toString());
  const [draftGpa, setDraftGpa] = useState(profile?.gpa?.toString() ?? '');
  const [draftAct, setDraftAct] = useState(profile?.act_score?.toString() ?? '');
  const [draftSat, setDraftSat] = useState(profile?.sat_score?.toString() ?? '');
  const [draftInterest, setDraftInterest] = useState('');
  const [draftTone, setDraftTone] = useState<'formal' | 'balanced' | 'direct'>('balanced');
  const [draftSubject, setDraftSubject] = useState('');
  const [draftBody, setDraftBody] = useState('');
  const [draftLoading, setDraftLoading] = useState(false);
  const [draftError, setDraftError] = useState('');

  // Close & reset drafter modal handler
  const closeModal = () => {
    setSelectedProgram(null);
    setDraftStep('staff');
    setDraftInterest('');
    setDraftSubject('');
    setDraftBody('');
    setDraftError('');
    setDraftLoading(false);
  };

  // Generate Email Handler
  const generateEmail = async () => {
    if (!selectedProgram) return;
    const hc = selectedProgram.head_coach;
    if (!hc) return;

    setDraftLoading(true);
    setDraftError('');

    try {
      const res = await fetch('/api/draft-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          coachFirstName: hc.first_name,
          coachLastName: hc.last_name,
          schoolName: selectedProgram.school_name,
          conference: selectedProgram.conference,
          region: selectedProgram.region,
          profile: {
            ...profile,
            gpa: draftGpa ? parseFloat(draftGpa) : undefined,
            act_score: draftAct ? parseInt(draftAct) : undefined,
            sat_score: draftSat ? parseInt(draftSat) : undefined,
          },
          gradYear: parseInt(draftGradYear),
          programInterest: draftInterest,
          tone: draftTone,
        }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      setDraftSubject(data.subject);
      setDraftBody(data.body);
      setDraftStep('draft');
    } catch (err: any) {
      setDraftError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setDraftLoading(false);
    }
  };

  // Sort state
  type SortKey = 'school_name' | 'conference' | 'state';
  const [sortKey, setSortKey] = useState<SortKey>('school_name');
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(a => !a);
    else { setSortKey(key); setSortAsc(true); }
  };

  // Dynamic Conference List
  const conferences = useMemo(() => {
    const set = new Set(programs.map(p => p.conference));
    return ['All', ...Array.from(set).sort()];
  }, [programs]);

  // Client-side Filtering + Sorting
  const filtered = useMemo(() => {
    const results = programs.filter(p => {
      const q = search.toLowerCase();
      const matchesSearch = !q ||
        p.school_name.toLowerCase().includes(q) ||
        p.conference.toLowerCase().includes(q) ||
        (p.head_coach && `${p.head_coach.first_name} ${p.head_coach.last_name}`.toLowerCase().includes(q));
      const matchesRegion = region === 'All' || p.region === region;
      const matchesConference = conference === 'All' || p.conference === conference;
      const matchesEmail = !emailOnly || p.has_email;
      return matchesSearch && matchesRegion && matchesConference && matchesEmail;
    });
    return results.sort((a, b) => {
      const av = (a[sortKey] ?? '').toLowerCase();
      const bv = (b[sortKey] ?? '').toLowerCase();
      return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
    });
  }, [programs, search, region, conference, emailOnly, sortKey, sortAsc]);

  return (
    <div className="space-y-10 max-w-4xl mx-auto">
      {/* Section 1: Page Header */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-black tracking-tight text-white">
            🎯 Recruiting Hub
          </h1>
          <Badge className="bg-primary/15 text-primary border border-primary/30 text-xs font-bold px-2.5 py-1">
            212 D1 Programs · 686 Coaches
          </Badge>
        </div>
        <p className="text-muted-foreground text-sm max-w-2xl leading-relaxed">
          Search 212 D1 programs, find coaching staff contact info, and start building your recruiting list.
        </p>
      </div>

      {/* Section 2: Profile Context Strip */}
      {profile && (
        <Card className="border-border/50 bg-card/40">
          <CardContent className="py-3 px-5 flex items-center justify-between">
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span>Searching as:</span>
              <span className="text-white font-semibold">{position}</span>
              <span>·</span>
              <span className="text-white font-semibold">Class of {gradYear}</span>
              <span>·</span>
              <span className="text-white font-semibold">{profile.target_level}</span>
            </div>
            <Link href="/profile" className="text-xs text-primary hover:underline">
              Update Profile →
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Section 3: Search + Filters */}
      <div className="space-y-3">
        {/* Search bar */}
        <Input
          placeholder="Search programs... (e.g. Notre Dame, Stanford, ACC)"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="bg-card/40 border-border/50 text-white placeholder:text-muted-foreground/50 h-11"
        />

        {/* Filter row */}
        <div className="flex flex-wrap gap-2 items-center w-full">
          {/* Region select */}
          <select
            value={region}
            onChange={e => setRegion(e.target.value)}
            className="h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {REGIONS.map(r => (
              <option key={r} value={r}>
                {r === 'All' ? 'All Regions' : r}
              </option>
            ))}
          </select>

          {/* Conference select */}
          <select
            value={conference}
            onChange={e => setConference(e.target.value)}
            className="h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary max-w-xs"
          >
            {conferences.map(c => (
              <option key={c} value={c}>
                {c === 'All' ? 'All Conferences' : c}
              </option>
            ))}
          </select>

          {/* Email toggle button */}
          <button
            onClick={() => setEmailOnly(!emailOnly)}
            className={cn(
              "h-9 px-3 rounded-md border text-xs font-semibold transition-colors cursor-pointer",
              emailOnly
                ? "border-primary bg-primary/15 text-primary"
                : "border-border/50 bg-card/40 text-muted-foreground hover:text-white"
            )}
          >
            ✉ Email Available
          </button>

          {/* Results count - pushed right */}
          <span className="ml-auto text-xs text-muted-foreground">
            {filtered.length} of {programs.length} programs
          </span>
        </div>
      </div>

      {/* Section 4: Results Table */}
      <div className="rounded-xl border border-border/50 overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-[2fr_2fr_1fr_2fr_1fr] gap-0 bg-secondary/30 border-b border-border/50 px-4 py-2.5">
          {([
            { label: 'School', key: 'school_name' },
            { label: 'Conference', key: 'conference' },
            { label: 'State', key: 'state' },
            { label: 'Head Coach', key: null },
            { label: 'Contact', key: null },
          ] as { label: string; key: SortKey | null }[]).map(col => (
            <button
              key={col.label}
              onClick={() => col.key && handleSort(col.key)}
              className={cn(
                'text-left text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1',
                col.key ? 'hover:text-white cursor-pointer' : 'cursor-default',
              )}
            >
              {col.label}
              {col.key && sortKey === col.key && (
                <span className="text-primary">{sortAsc ? '↑' : '↓'}</span>
              )}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground text-sm">
            No programs match your filters — try broadening your search.
          </div>
        ) : (
          <div className="divide-y divide-border/30 max-h-[520px] overflow-y-auto">
            {filtered.map(program => {
              const hc = program.head_coach;
              return (
                <div
                  key={program.program_id}
                  onClick={() => setSelectedProgram(program)}
                  className="grid grid-cols-[2fr_2fr_1fr_2fr_1fr] gap-0 px-4 py-3 hover:bg-card/60 cursor-pointer transition-colors group items-center"
                >
                  {/* School */}
                  <p className="text-sm font-semibold text-white group-hover:text-primary transition-colors truncate pr-3">
                    {program.school_name}
                  </p>
                  {/* Conference */}
                  <p className="text-xs text-muted-foreground truncate pr-3">
                    {program.conference}
                  </p>
                  {/* State */}
                  <p className="text-xs text-muted-foreground">
                    {program.state}
                  </p>
                  {/* Head Coach */}
                  <p className="text-xs text-muted-foreground truncate pr-3">
                    {hc ? `${hc.first_name} ${hc.last_name}` : <span className="italic opacity-40">No info</span>}
                  </p>
                  {/* Contact */}
                  <div className="flex items-center gap-2">
                    {hc?.email ? (
                      <a
                        href={`mailto:${hc.email}`}
                        onClick={e => e.stopPropagation()}
                        className="text-[10px] text-primary hover:underline truncate"
                        title={hc.email}
                      >
                        ✉ Email
                      </a>
                    ) : (
                      <span className="text-[10px] text-muted-foreground/40 italic">—</span>
                    )}
                    <span className="text-[10px] text-muted-foreground/50 group-hover:text-primary transition-colors ml-auto">
                      →
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer */}
        <div className="px-4 py-2 bg-secondary/20 border-t border-border/30">
          <p className="text-[10px] text-muted-foreground">
            {filtered.length} of {programs.length} programs · Click any row to view staff & draft email
          </p>
        </div>
      </div>

      {/* Section 5: Staff Detail Modal / Email Drafter Wizard */}
      {selectedProgram && (
        <Dialog onClose={closeModal}>
          {/* Header */}
          <div className="p-6 border-b border-border/30 space-y-1">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">{selectedProgram.school_name}</h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {selectedProgram.conference} · {selectedProgram.state} · {selectedProgram.region}
                </p>
              </div>
              <button onClick={closeModal} className="text-muted-foreground hover:text-white p-1 cursor-pointer">✕</button>
            </div>
            {selectedProgram.program_url && (
              <a
                href={selectedProgram.program_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline block mt-1"
              >
                {selectedProgram.program_url.replace('https://', '')} ↗
              </a>
            )}
          </div>

          {/* Modal Multi-Step Views */}
          {draftStep === 'staff' && (
            <>
              {/* Staff list - scrollable */}
              <div className="overflow-y-auto flex-1 p-6 space-y-6 max-h-[50vh]">
                {(['Head Coach', 'Assistant Coach', 'Director of Operations'] as const).map(titleGroup => {
                  const coaches = selectedProgram.coaches.filter(c => c.title === titleGroup);
                  if (coaches.length === 0) return null;

                  return (
                    <div key={titleGroup} className="space-y-3">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                        {pluralizeTitle(titleGroup, coaches.length)}{coaches.length > 1 && titleGroup === 'Head Coach' ? 'ES' : ''}
                      </p>
                      {coaches.map(coach => (
                        <CoachRow key={coach.coach_id} coach={coach} />
                      ))}
                    </div>
                  );
                })}

                {selectedProgram.coaches.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No staff info available for this program.
                  </p>
                )}
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-border/30 flex gap-3">
                <Button
                  size="sm"
                  onClick={() => setDraftStep('form')}
                  disabled={!selectedProgram?.head_coach}
                  className="font-semibold cursor-pointer"
                  title={!selectedProgram?.head_coach ? "No head coach on file" : undefined}
                >
                  ✉ Draft Email
                </Button>
                {selectedProgram.program_url && (
                  <Button asChild size="sm" variant="outline" className="border-border/50 font-semibold cursor-pointer">
                    <a href={selectedProgram.program_url} target="_blank" rel="noopener noreferrer">
                      Visit Website ↗
                    </a>
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  className="border-border/50 font-semibold cursor-pointer"
                  onClick={() => {
                    if (!selectedProgram?.head_coach) return;
                    setPrefilledOutreach({
                      school_name: selectedProgram.school_name,
                      coach_name: `${selectedProgram.head_coach.first_name} ${selectedProgram.head_coach.last_name}`,
                      coach_title: selectedProgram.head_coach.title,
                      coach_email: selectedProgram.head_coach.email ?? null,
                    });
                    closeModal();
                    // Scroll to tracker
                    setTimeout(() => {
                      document.getElementById('outreach-tracker')?.scrollIntoView({ behavior: 'smooth' });
                    }, 100);
                  }}
                >
                  📋 Track Outreach
                </Button>
              </div>
            </>
          )}

          {draftStep === 'form' && (
            <>
              {/* Scrollable Form Body */}
              <div className="overflow-y-auto flex-1 p-6 space-y-5 max-h-[50vh]">
                <div className="space-y-1">
                  <p className="text-xs font-bold text-white">
                    Drafting email to Coach {selectedProgram.head_coach?.last_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {selectedProgram.school_name} · {selectedProgram.conference}
                  </p>
                </div>

                {/* Grad Year */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Graduation Year
                  </label>
                  <input
                    type="number"
                    value={draftGradYear}
                    onChange={e => setDraftGradYear(e.target.value)}
                    className="w-full h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="e.g. 2027"
                  />
                </div>

                {/* Academics row */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Academics <span className="text-muted-foreground/50 normal-case font-normal">(optional — included in email if provided)</span>
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="space-y-1">
                      <p className="text-[10px] text-muted-foreground">GPA</p>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="5"
                        value={draftGpa}
                        onChange={e => setDraftGpa(e.target.value)}
                        className="w-full h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="3.8"
                      />
                    </div>
                    <div className="space-y-1">
                      <p className="text-[10px] text-muted-foreground">ACT</p>
                      <input
                        type="number"
                        min="1"
                        max="36"
                        value={draftAct}
                        onChange={e => setDraftAct(e.target.value)}
                        className="w-full h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="29"
                      />
                    </div>
                    <div className="space-y-1">
                      <p className="text-[10px] text-muted-foreground">SAT</p>
                      <input
                        type="number"
                        min="400"
                        max="1600"
                        value={draftSat}
                        onChange={e => setDraftSat(e.target.value)}
                        className="w-full h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="1280"
                      />
                    </div>
                  </div>
                </div>

                {/* Program interest */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Why this program? <span className="text-muted-foreground/50 normal-case font-normal">(1–3 sentences)</span>
                  </label>
                  <textarea
                    value={draftInterest}
                    onChange={e => setDraftInterest(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 rounded-md border border-border/50 bg-card/60 text-sm text-white placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-primary resize-none"
                    placeholder="e.g. I attended your ID camp in June and was impressed by your style of play. I follow the program closely and feel the conference level matches my goals..."
                  />
                </div>

                {/* Tone selector */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Tone
                  </label>
                  <div className="flex gap-2">
                    {(['formal', 'balanced', 'direct'] as const).map(t => (
                      <button
                        key={t}
                        onClick={() => setDraftTone(t)}
                        className={cn(
                          "flex-1 h-9 rounded-md border text-xs font-semibold capitalize transition-colors cursor-pointer",
                          draftTone === t
                            ? "border-primary bg-primary/15 text-primary"
                            : "border-border/50 bg-card/40 text-muted-foreground hover:text-white"
                        )}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                  <p className="text-[10px] text-muted-foreground/60 leading-normal">
                    {draftTone === 'formal' && 'Measured and academic-forward. Best for Ivy-adjacent and academic programs.'}
                    {draftTone === 'balanced' && 'Professional but warm. Works well for most D1 programs.'}
                    {draftTone === 'direct' && 'Confident and athletics-first. Best for programs that prioritize results.'}
                  </p>
                </div>

                {draftError && (
                  <p className="text-xs text-destructive font-medium">{draftError}</p>
                )}
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-border/30 flex gap-3">
                <Button
                  size="sm"
                  variant="outline"
                  className="border-border/50 font-semibold cursor-pointer"
                  onClick={() => {
                    setDraftStep('staff');
                    setDraftError('');
                  }}
                >
                  ← Back
                </Button>
                <Button
                  size="sm"
                  className="font-semibold flex-1 cursor-pointer"
                  onClick={generateEmail}
                  disabled={draftLoading}
                >
                  {draftLoading ? 'Generating...' : 'Generate Email →'}
                </Button>
              </div>
            </>
          )}

          {draftStep === 'draft' && (
            <>
              {/* Scrollable Draft Body */}
              <div className="overflow-y-auto flex-1 p-6 space-y-4 max-h-[50vh]">
                {/* Subject line */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={draftSubject}
                    onChange={e => setDraftSubject(e.target.value)}
                    className="w-full h-9 px-3 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>

                {/* Email body */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                    Email Body
                  </label>
                  <textarea
                    value={draftBody}
                    onChange={e => setDraftBody(e.target.value)}
                    rows={10}
                    className="w-full px-3 py-2 rounded-md border border-border/50 bg-card/60 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary resize-none leading-relaxed"
                  />
                </div>

                {draftError && (
                  <p className="text-xs text-destructive font-medium">{draftError}</p>
                )}

                <p className="text-[10px] text-muted-foreground/50">
                  Edit freely — this is your email. Copy and paste into Gmail, Outlook, or any email client.
                </p>
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-border/30 flex gap-2 flex-wrap">
                <Button
                  size="sm"
                  variant="outline"
                  className="border-border/50 font-semibold cursor-pointer"
                  onClick={() => setDraftStep('form')}
                >
                  ← Edit Details
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-border/50 font-semibold cursor-pointer"
                  onClick={generateEmail}
                  disabled={draftLoading}
                >
                  {draftLoading ? '...' : '🔄 Regenerate'}
                </Button>
                <CopyEmailButton subject={draftSubject} body={draftBody} />
              </div>
            </>
          )}
        </Dialog>
      )}

      <div id="outreach-tracker">
        <OutreachTracker
          outreachLog={outreachLog}
          prefilled={prefilledOutreach}
          onPrefilledUsed={() => setPrefilledOutreach(null)}
        />
      </div>

      <hr className="border-border/30 my-8" />

      {/* Section 6: Email Drafter Preview & Info (kept from original) */}
      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {FEATURES.map((feature) => (
          <Card key={feature.title} className="border-border/50 bg-card/40 backdrop-blur-sm">
            <CardContent className="p-5 space-y-3">
              <div className="text-3xl">{feature.icon}</div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-bold text-white">{feature.title}</p>
                  <span className="text-[10px] font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                    {feature.stat}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Sample Email Preview */}
      <div className="space-y-3">
        <div>
          <h2 className="text-lg font-bold text-white">What Your Recruiting Email Will Look Like</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Your Player AI profile auto-fills every bracket. You personalize, review, and send.
          </p>
        </div>

        <Card className="border-primary/20 bg-card/40 overflow-hidden">
          {/* Email header bar */}
          <div className="bg-secondary/30 border-b border-border/30 px-5 py-3 space-y-1">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">To:</span>
              <span className="text-primary">coach@university.edu</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">Subject:</span>
              <span>{position} Prospect — {name} — Class of {gradYear}</span>
            </div>
          </div>

          {/* Email body */}
          <CardContent className="p-5">
            <div className="text-sm text-muted-foreground leading-relaxed space-y-3 font-mono text-xs">
              <p>Coach [Last Name],</p>
              <p>
                My name is <span className="text-primary font-semibold">{name}</span> and
                I am a <span className="text-primary font-semibold">{level} {position}</span> graduating
                in <span className="text-primary font-semibold">{gradYear}</span>. I have been
                researching programs that compete at the highest level and I am very interested
                in learning more about your program and any opportunities that may exist.
              </p>
              <p>
                I am currently training with a focus on{' '}
                <span className="text-primary font-semibold">
                  {profile?.focus_areas?.slice(0, 2).join(' and ') ?? 'distribution and positioning'}
                </span>.
                My highlight reel and full profile are available through Player AI.
              </p>
              <p>
                I would welcome the opportunity to connect at your convenience — whether by
                phone, at an upcoming ID camp, or at a tournament where your staff may be
                present. Thank you for your time and consideration.
              </p>
              <p>
                Respectfully,<br />
                <span className="text-primary font-semibold">{name}</span><br />
                <span className="text-muted-foreground/60">{position} · Class of {gradYear}</span>
              </p>
            </div>

            {/* Overlay label */}
            <div className="mt-4 flex items-center gap-2 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <span className="text-yellow-400 text-xs">⚡</span>
              <p className="text-xs text-yellow-400 font-medium">
                Example preview — highlighted fields auto-fill from your Player AI profile when this feature launches.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* How it works timeline */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold text-white">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          {[
            { step: '1', title: 'Complete Your Profile', desc: 'Your position, level, focus areas, and highlight reel — already in Player AI' },
            { step: '2', title: 'Find Your Programs', desc: 'Search and filter 212 D1 programs by division, region, and conference' },
            { step: '3', title: 'Draft Your Email', desc: 'AI generates a personalized email using your profile in seconds' },
            { step: '4', title: 'Track Everything', desc: 'Log every contact, response, and follow-up in one organized view' },
          ].map((item) => (
            <Card key={item.step} className="border-border/50 bg-card/40">
              <CardContent className="p-4 space-y-2">
                <div className="text-2xl font-black text-primary">{item.step}</div>
                <p className="text-xs font-bold text-white">{item.title}</p>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 space-y-3">
        <h3 className="text-lg font-bold text-white">While You Wait — Get Your Profile Ready</h3>
        <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
          The stronger your Player AI profile, the better your recruiting emails will be when this feature launches. Make sure your highlight reel is uploaded, your focus areas are accurate, and your position and level reflect where you are right now.
        </p>
        <div className="flex flex-wrap gap-3 pt-1">
          <Button asChild size="sm" className="font-semibold cursor-pointer">
            <Link href="/reel">Build Your Highlight Reel →</Link>
          </Button>
          <Button asChild size="sm" variant="outline" className="font-semibold border-border/50 cursor-pointer">
            <Link href="/profile">Update Your Profile →</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}


function CoachRow({ coach }: { coach: CoachRecord }) {
  const [copied, setCopied] = useState(false);

  const copyEmail = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!coach.email) return;
    navigator.clipboard.writeText(coach.email);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-0.5">
      <div className="flex items-center gap-1.5">
        <p className="text-sm font-semibold text-white">
          {coach.first_name} {coach.last_name}
        </p>
        {coach.position_focus && (
          <Badge className="bg-primary/10 text-primary border-0 text-[9px] font-medium h-4 px-1 py-0 flex items-center">
            {coach.position_focus}
          </Badge>
        )}
      </div>
      {coach.email && (
        <div className="flex items-center gap-2">
          <a
            href={`mailto:${coach.email}`}
            className="text-xs text-primary hover:underline truncate"
            onClick={e => e.stopPropagation()}
          >
            {coach.email}
          </a>
          <button
            onClick={copyEmail}
            className="shrink-0 text-[10px] text-muted-foreground hover:text-white transition-colors cursor-pointer"
            title="Copy email"
          >
            {copied ? '✓' : '📋'}
          </button>
        </div>
      )}
      {coach.phone && (
        <p className="text-xs text-muted-foreground">{coach.phone}</p>
      )}
      {!coach.email && !coach.phone && (
        <p className="text-xs text-muted-foreground/40 italic">No contact info on file</p>
      )}
    </div>
  );
}

function CopyEmailButton({ subject, body }: { subject: string; body: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const full = `Subject: ${subject}\n\n${body}`;
    navigator.clipboard.writeText(full);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <Button
      size="sm"
      className="font-semibold flex-1 cursor-pointer"
      onClick={handleCopy}
    >
      {copied ? '✓ Copied!' : '📋 Copy Email'}
    </Button>
  );
}
