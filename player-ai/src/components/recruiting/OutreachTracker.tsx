'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import type { OutreachLog, OutreachEntry, OutreachStatus } from '@/lib/types/recruiting';
import { saveOutreachEntryAction, deleteOutreachEntryAction } from '@/lib/actions/recruiting';

interface OutreachTrackerProps {
  outreachLog: OutreachLog;
  prefilled: {
    school_name: string;
    coach_name: string;
    coach_title: string;
    coach_email: string | null;
  } | null;
  onPrefilledUsed: () => void;
}

const STATUS_CONFIG: Record<OutreachStatus, { label: string; color: string; dot: string }> = {
  emailed:        { label: 'Emailed',         color: 'text-blue-400',   dot: 'bg-blue-400' },
  responded:      { label: 'Responded',        color: 'text-green-400',  dot: 'bg-green-400' },
  call_scheduled: { label: 'Call Scheduled',   color: 'text-yellow-400', dot: 'bg-yellow-400' },
  visited:        { label: 'Visited',          color: 'text-purple-400', dot: 'bg-purple-400' },
  not_interested: { label: 'Not Interested',   color: 'text-red-400',    dot: 'bg-red-400' },
  committed:      { label: 'Committed',         color: 'text-primary',    dot: 'bg-primary' },
};

function FormLabel({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className="text-xs font-semibold text-muted-foreground tracking-wide uppercase block mb-1">
      {children}
    </label>
  );
}

export default function OutreachTracker({ outreachLog, prefilled, onPrefilledUsed }: OutreachTrackerProps) {
  const today = new Date().toISOString().split('T')[0];

  const [entries, setEntries] = useState<OutreachEntry[]>(outreachLog.entries || []);
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState<OutreachEntry | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Form fields
  const [formSchool, setFormSchool] = useState('');
  const [formCoachName, setFormCoachName] = useState('');
  const [formCoachTitle, setFormCoachTitle] = useState<'Head Coach' | 'Assistant Coach' | 'Director of Operations'>('Head Coach');
  const [formCoachEmail, setFormCoachEmail] = useState('');
  const [formDate, setFormDate] = useState(today);
  const [formStatus, setFormStatus] = useState<OutreachStatus>('emailed');
  const [formFollowUp, setFormFollowUp] = useState('');
  const [formNotes, setFormNotes] = useState('');

  // Update entries state if database updates outreachLog prop
  useEffect(() => {
    setEntries(outreachLog.entries || []);
  }, [outreachLog]);

  // Prefilled event handler
  useEffect(() => {
    if (prefilled) {
      setFormSchool(prefilled.school_name);
      setFormCoachName(prefilled.coach_name);
      // Safeguard against non-exact title matchups
      const title = prefilled.coach_title;
      if (title === 'Head Coach' || title === 'Assistant Coach' || title === 'Director of Operations') {
        setFormCoachTitle(title);
      } else {
        setFormCoachTitle('Head Coach');
      }
      setFormCoachEmail(prefilled.coach_email ?? '');
      setFormDate(today);
      setFormStatus('emailed');
      setFormFollowUp('');
      setFormNotes('');
      setEditingEntry(null);
      setShowForm(true);
      onPrefilledUsed();
    }
  }, [prefilled, today, onPrefilledUsed]);

  // Reset form fields helper
  const resetForm = () => {
    setFormSchool('');
    setFormCoachName('');
    setFormCoachTitle('Head Coach');
    setFormCoachEmail('');
    setFormDate(today);
    setFormStatus('emailed');
    setFormFollowUp('');
    setFormNotes('');
    setEditingEntry(null);
    setError('');
  };

  // Save entry handler
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formSchool.trim() || !formCoachName.trim()) {
      setError('School name and coach name are required.');
      return;
    }

    setSaving(true);
    setError('');

    const entry: OutreachEntry = {
      id: editingEntry?.id ?? crypto.randomUUID(),
      school_name: formSchool.trim(),
      coach_name: formCoachName.trim(),
      coach_title: formCoachTitle,
      coach_email: formCoachEmail.trim() || null,
      contacted_date: formDate,
      status: formStatus,
      notes: formNotes.trim(),
      follow_up_date: formFollowUp || null,
      created_at: editingEntry?.created_at ?? new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const result = await saveOutreachEntryAction(entry);
    if (result.success) {
      // Optimistic update
      setEntries(prev => {
        const idx = prev.findIndex(e => e.id === entry.id);
        if (idx !== -1) {
          const updated = [...prev];
          updated[idx] = entry;
          return updated;
        }
        return [entry, ...prev];
      });
      resetForm();
      setShowForm(false);
    } else {
      setError(result.error ?? 'Failed to save entry.');
    }
    setSaving(false);
  };

  // Delete entry handler
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this outreach record?')) return;
    const result = await deleteOutreachEntryAction(id);
    if (result.success) {
      setEntries(prev => prev.filter(e => e.id !== id));
    } else {
      alert(result.error ?? 'Failed to delete entry.');
    }
  };

  // Edit entry handler
  const handleEdit = (entry: OutreachEntry) => {
    setEditingEntry(entry);
    setFormSchool(entry.school_name);
    setFormCoachName(entry.coach_name);
    setFormCoachTitle(entry.coach_title as any);
    setFormCoachEmail(entry.coach_email ?? '');
    setFormDate(entry.contacted_date);
    setFormStatus(entry.status);
    setFormFollowUp(entry.follow_up_date ?? '');
    setFormNotes(entry.notes);
    setShowForm(true);
    setError('');
  };

  // Summary Metrics
  const uniqueSchoolsCount = useMemo(() => {
    const set = new Set(entries.map(e => e.school_name.toLowerCase().trim()));
    return set.size;
  }, [entries]);

  const responsesCount = useMemo(() => {
    const responseStatuses: OutreachStatus[] = ['responded', 'call_scheduled', 'visited', 'committed'];
    return entries.filter(e => responseStatuses.includes(e.status)).length;
  }, [entries]);

  // Display entries sorted by contacted date descending
  const sortedEntries = useMemo(() => {
    return [...entries].sort((a, b) => b.contacted_date.localeCompare(a.contacted_date));
  }, [entries]);

  // Check if follow up date is past/overdue compared to today
  const isFollowUpOverdue = (dateStr: string | null) => {
    if (!dateStr) return false;
    return dateStr < today;
  };

  const formatDateString = (dateStr: string) => {
    try {
      const [year, month, day] = dateStr.split('-');
      return `${month}/${day}/${year.slice(2)}`;
    } catch {
      return dateStr;
    }
  };

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-sm shadow-xl rounded-xl">
      <CardHeader className="p-6 pb-3 border-b border-border/30">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Outreach Tracker
            </CardTitle>
            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1 font-semibold">
              <span className="text-white">{uniqueSchoolsCount}</span> {uniqueSchoolsCount === 1 ? 'school' : 'schools'} contacted
              <span>·</span>
              <span className="text-primary">{responsesCount}</span> {responsesCount === 1 ? 'response' : 'responses'}
            </div>
          </div>
          {!showForm && (
            <Button
              size="sm"
              onClick={() => {
                resetForm();
                setShowForm(true);
              }}
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-3 py-1.5 h-8 text-xs rounded-lg cursor-pointer"
            >
              + Log Contact
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Inline Form */}
        {showForm && (
          <form onSubmit={handleSave} className="bg-secondary/10 border border-border/50 rounded-xl p-4 space-y-4 animate-in fade-in duration-200">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              {editingEntry ? 'Edit Outreach Log' : 'Log New Contact'}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <FormLabel htmlFor="formSchool">School Name</FormLabel>
                <Input
                  id="formSchool"
                  type="text"
                  required
                  placeholder="e.g. UCLA"
                  value={formSchool}
                  onChange={e => setFormSchool(e.target.value)}
                  className="bg-secondary/20 border-border/50 text-sm h-8 rounded-lg"
                />
              </div>

              <div>
                <FormLabel htmlFor="formCoachName">Coach Name</FormLabel>
                <Input
                  id="formCoachName"
                  type="text"
                  required
                  placeholder="e.g. John Smith"
                  value={formCoachName}
                  onChange={e => setFormCoachName(e.target.value)}
                  className="bg-secondary/20 border-border/50 text-sm h-8 rounded-lg"
                />
              </div>

              <div>
                <FormLabel htmlFor="formCoachTitle">Title</FormLabel>
                <select
                  id="formCoachTitle"
                  value={formCoachTitle}
                  onChange={e => setFormCoachTitle(e.target.value as any)}
                  className="h-8 w-full rounded-lg border border-border/50 bg-secondary/20 px-2.5 py-1 text-sm outline-none text-foreground cursor-pointer"
                >
                  <option value="Head Coach">Head Coach</option>
                  <option value="Assistant Coach">Assistant Coach</option>
                  <option value="Director of Operations">Director of Operations</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <FormLabel htmlFor="formCoachEmail">Coach Email</FormLabel>
                <Input
                  id="formCoachEmail"
                  type="email"
                  placeholder="e.g. coach@school.edu"
                  value={formCoachEmail}
                  onChange={e => setFormCoachEmail(e.target.value)}
                  className="bg-secondary/20 border-border/50 text-sm h-8 rounded-lg"
                />
              </div>

              <div>
                <FormLabel htmlFor="formDate">Date Contacted</FormLabel>
                <Input
                  id="formDate"
                  type="date"
                  required
                  value={formDate}
                  onChange={e => setFormDate(e.target.value)}
                  className="bg-secondary/20 border-border/50 text-sm h-8 rounded-lg"
                />
              </div>

              <div>
                <FormLabel htmlFor="formStatus">Status</FormLabel>
                <select
                  id="formStatus"
                  value={formStatus}
                  onChange={e => setFormStatus(e.target.value as any)}
                  className="h-8 w-full rounded-lg border border-border/50 bg-secondary/20 px-2.5 py-1 text-sm outline-none text-foreground cursor-pointer"
                >
                  {Object.entries(STATUS_CONFIG).map(([k, v]) => (
                    <option key={k} value={k}>{v.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <FormLabel htmlFor="formFollowUp">
                  Follow-up Date <span className="text-[10px] text-muted-foreground/60 font-normal lowercase">(optional)</span>
                </FormLabel>
                <Input
                  id="formFollowUp"
                  type="date"
                  value={formFollowUp}
                  onChange={e => setFormFollowUp(e.target.value)}
                  className="bg-secondary/20 border-border/50 text-sm h-8 rounded-lg"
                />
              </div>

              <div className="md:col-span-3">
                <FormLabel htmlFor="formNotes">Notes / Response details</FormLabel>
                <textarea
                  id="formNotes"
                  rows={2}
                  placeholder="Drafted email generated from highlight reel, waiting on response..."
                  value={formNotes}
                  onChange={e => setFormNotes(e.target.value)}
                  className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-1.5 text-sm outline-none text-foreground resize-none leading-normal placeholder:text-muted-foreground/35"
                />
              </div>
            </div>

            {error && <p className="text-xs text-destructive font-medium">{error}</p>}

            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  resetForm();
                  setShowForm(false);
                }}
                disabled={saving}
                className="border-border/50 font-semibold h-8 text-xs cursor-pointer px-4 rounded-lg"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving}
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold h-8 text-xs cursor-pointer px-5 rounded-lg"
              >
                {saving ? 'Saving...' : 'Save Entry'}
              </Button>
            </div>
          </form>
        )}

        {/* Entries list */}
        {sortedEntries.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-border/40 rounded-xl space-y-2">
            <span className="text-2xl block">✉️</span>
            <p className="text-xs font-semibold text-white">No outreach logged yet</p>
            <p className="text-[11px] text-muted-foreground max-w-xs mx-auto leading-relaxed">
              Find a program above and click "Track Outreach" to pre-fill their info here, or click "+ Log Contact" to add manually.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden border border-border/40 rounded-xl divide-y divide-border/30">
            {sortedEntries.map(entry => {
              const status = STATUS_CONFIG[entry.status] || STATUS_CONFIG.emailed;
              const overdue = isFollowUpOverdue(entry.follow_up_date);

              return (
                <div key={entry.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/20 hover:bg-card/40 transition-colors">
                  <div className="space-y-1.5 flex-1 min-w-0">
                    {/* Status & School */}
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={cn("inline-flex items-center gap-1.5 text-xs font-bold px-2 py-0.5 rounded-full bg-secondary/80 border border-border/20", status.color)}>
                        <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", status.dot)} />
                        {status.label}
                      </span>
                      <p className="text-sm font-bold text-white truncate">{entry.school_name}</p>
                    </div>

                    {/* Coach Details */}
                    <div className="text-xs text-muted-foreground flex flex-wrap items-center gap-2">
                      <span className="text-white font-semibold">{entry.coach_name}</span>
                      <span>·</span>
                      <span>{entry.coach_title}</span>
                      {entry.coach_email && (
                        <>
                          <span>·</span>
                          <a href={`mailto:${entry.coach_email}`} className="text-primary hover:underline truncate">
                            {entry.coach_email}
                          </a>
                        </>
                      )}
                    </div>

                    {/* Notes preview */}
                    {entry.notes && (
                      <p className="text-xs text-muted-foreground/85 leading-relaxed bg-secondary/5 border border-border/15 p-2 rounded-lg max-w-xl italic">
                        {entry.notes}
                      </p>
                    )}
                  </div>

                  {/* Actions & Dates */}
                  <div className="flex flex-row md:flex-col md:items-end justify-between md:justify-center gap-2 shrink-0">
                    <div className="text-[11px] text-muted-foreground text-left md:text-right space-y-0.5 font-medium">
                      <p>Contacted: {formatDateString(entry.contacted_date)}</p>
                      {entry.follow_up_date && (
                        <p className={cn(overdue ? "text-yellow-400 font-bold" : "text-muted-foreground")}>
                          {overdue ? "! Follow up: " : "Follow up: "}{formatDateString(entry.follow_up_date)}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleEdit(entry)}
                        className="text-muted-foreground hover:text-white transition-colors cursor-pointer text-xs p-1"
                        title="Edit entry"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="text-muted-foreground hover:text-destructive transition-colors cursor-pointer text-xs p-1"
                        title="Delete entry"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
