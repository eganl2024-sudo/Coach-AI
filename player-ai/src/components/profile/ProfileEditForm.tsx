'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { updateProfileAction } from '@/lib/actions/training';
import type { AthleteProfile } from '@/lib/types/player';
import { LEAGUES_BY_LEVEL } from '@/lib/constants/leagues';

interface ProfileEditFormProps {
  profile: AthleteProfile;
  username: string;
}

function FormLabel({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className="text-xs font-semibold text-muted-foreground tracking-wide uppercase block mb-1.5">
      {children}
    </label>
  );
}

function FormSelect({ className, children, ...props }: React.ComponentProps<'select'>) {
  return (
    <div className="relative w-full">
      <select
        className={cn(
          "h-8 w-full rounded-lg border border-border/50 bg-secondary/20 px-2.5 py-1 text-sm outline-none transition-all focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20 text-foreground cursor-pointer appearance-none pr-8",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2.5 text-muted-foreground">
        <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

const deriveAgeGroup = (age: number): string => {
  if (age <= 12) return 'U12';
  if (age <= 13) return 'U13';
  if (age <= 14) return 'U14';
  if (age <= 15) return 'U15';
  if (age <= 16) return 'U16';
  if (age <= 17) return 'U17';
  if (age <= 18) return 'U18';
  if (age <= 19) return 'U19';
  if (age <= 23) return 'U23';
  return 'Senior';
};

export default function ProfileEditForm({ profile, username }: ProfileEditFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<Partial<AthleteProfile>>({
    name: profile.name,
    age: profile.age,
    email: profile.email || '',
    age_group: profile.age_group,
    position: profile.position,
    secondary_position: profile.secondary_position,
    preferred_foot: profile.preferred_foot,
    level: profile.level,
    league: profile.league ?? '',
    club_name: profile.club_name ?? '',
    grad_year: profile.grad_year ?? new Date().getFullYear() + 3,
    game_days: profile.game_days ?? [],
    target_level: profile.target_level,
    sessions_per_week: profile.sessions_per_week,
    session_duration: profile.session_duration,
    focus_areas: profile.focus_areas || [],
    equipment_available: profile.equipment_available || [],
    gpa: profile.gpa ?? undefined,
    gpa_scale: profile.gpa_scale ?? '4.0',
    act_score: profile.act_score ?? undefined,
    sat_score: profile.sat_score ?? undefined,
  });

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRegenConfirm, setShowRegenConfirm] = useState(false);

  const PLAN_AFFECTING_FIELDS = [
    'position',
    'secondary_position',
    'level',
    'league',
    'game_days',
    'focus_areas',
    'equipment_available',
    'sessions_per_week',
    'session_duration',
  ];

  const planAffected = PLAN_AFFECTING_FIELDS.some(
    (f) => JSON.stringify(formData[f as keyof AthleteProfile]) !== JSON.stringify(profile[f as keyof AthleteProfile])
  );

  const handleAgeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newAge = parseInt(e.target.value) || 0;
    setFormData((prev) => ({
      ...prev,
      age: newAge,
      age_group: deriveAgeGroup(newAge),
    }));
  };

  const handleFocusClick = (area: string) => {
    const currentFocus = formData.focus_areas || [];
    const isSelected = currentFocus.includes(area);
    if (isSelected) {
      setFormData((prev) => ({
        ...prev,
        focus_areas: currentFocus.filter((a) => a !== area),
      }));
    } else {
      if (currentFocus.length < 3) {
        setFormData((prev) => ({
          ...prev,
          focus_areas: [...currentFocus, area],
        }));
      }
    }
  };

  const handleEquipmentClick = (eq: string) => {
    const currentEq = formData.equipment_available || [];
    const isSelected = currentEq.includes(eq);
    if (isSelected) {
      if (currentEq.length > 1) {
        setFormData((prev) => ({
          ...prev,
          equipment_available: currentEq.filter((e) => e !== eq),
        }));
      }
    } else {
      setFormData((prev) => ({
        ...prev,
        equipment_available: [...currentEq, eq],
      }));
    }
  };

  const handleSaveClick = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!formData.name?.trim()) {
      setError('Name is required.');
      return;
    }
    if (!formData.age || formData.age < 10 || formData.age > 22) {
      setError('Age must be between 10 and 22.');
      return;
    }
    if ((formData.focus_areas?.length || 0) === 0) {
      setError('Select at least one focus area.');
      return;
    }
    if (formData.gpa !== undefined && (formData.gpa < 0 || formData.gpa > 5)) {
      setError('GPA must be between 0.0 and 5.0.');
      return;
    }
    if (formData.act_score !== undefined && (formData.act_score < 1 || formData.act_score > 36)) {
      setError('ACT score must be between 1 and 36.');
      return;
    }
    if (formData.sat_score !== undefined && (formData.sat_score < 400 || formData.sat_score > 1600)) {
      setError('SAT score must be between 400 and 1600.');
      return;
    }

    if (planAffected) {
      setShowRegenConfirm(true);
    } else {
      saveProfile(false);
    }
  };

  const saveProfile = async (regeneratePlan: boolean) => {
    setSaving(true);
    setError(null);
    setShowRegenConfirm(false);
    try {
      // Sanitize email — trim whitespace, treat empty string as undefined
      const sanitizedFormData = {
        ...formData,
        email: formData.email?.toString().trim() || undefined,
      };
      const result = await updateProfileAction(sanitizedFormData, regeneratePlan);
      if (result.success) {
        setSaved(true);
        setTimeout(() => {
          setSaved(false);
        }, 2000);
        if (regeneratePlan) {
          router.push('/training');
        }
      } else {
        setError(result.error || 'Failed to update profile.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setSaving(false);
    }
  };

  const positions = [
    'Goalkeeper',
    'Center Back',
    'Full Back',
    'Defensive Midfielder',
    'Central Midfielder',
    'Attacking Midfielder',
    'Winger',
    'Striker',
  ];

  const levels = [
    'Recreational',
    'Competitive Club',
    'Academy/Select',
    'Varsity High School',
    'College',
    'Professional',
  ];

  const targetLevels = [
    'Competitive Club',
    'Academy/Select',
    'Varsity Starter',
    'College Prospect',
    'College Starter',
    'Professional Prospect',
    'Professional',
  ];

  const focusOptions = [
    'Finishing',
    'First Touch',
    '1v1 Attacking',
    '1v1 Defending',
    'Passing & Receiving',
    'Dribbling & Ball Mastery',
    'Crossing & Delivery',
    'Pressing & Defending',
    'Positioning',
    'Weak Foot Development',
    'Aerial Ability',
    'Long Range Shooting',
  ];

  const equipmentOptions = [
    'Ball only',
    'Cones',
    'Goal',
    'Rebounder/Wall',
    'Training Partner',
  ];

  const leaguesByLevel = LEAGUES_BY_LEVEL;

  const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const currentYear = new Date().getFullYear();
  const gradYears = Array.from({ length: 8 }, (_, i) => currentYear + i);

  return (
    <form onSubmit={handleSaveClick} className="space-y-6">
      {/* Section 1 — Player Identity */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold text-white">Player Identity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-4">
              <div>
                <FormLabel htmlFor="name">Name</FormLabel>
                <Input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  className="bg-secondary/20 border-border/50 text-sm h-8"
                />
              </div>
              <div>
                <FormLabel htmlFor="email">
                  Email Address{' '}
                  <span className="text-muted-foreground normal-case font-normal">
                    (optional — for weekly summary)
                  </span>
                </FormLabel>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email as string || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="bg-secondary/20 border-border/50 text-sm h-8"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <FormLabel htmlFor="age">Age</FormLabel>
                <Input
                  id="age"
                  type="number"
                  min={10}
                  max={22}
                  required
                  value={formData.age}
                  onChange={handleAgeChange}
                  className="bg-secondary/20 border-border/50 text-sm h-8"
                />
              </div>

              <div>
                <FormLabel htmlFor="age_group">Age Group</FormLabel>
                <FormSelect
                  id="age_group"
                  value={formData.age_group}
                  onChange={(e) => setFormData((prev) => ({ ...prev, age_group: e.target.value }))}
                >
                  {['U12', 'U13', 'U14', 'U15', 'U16', 'U17', 'U18', 'U19', 'U23', 'Senior'].map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </FormSelect>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <FormLabel htmlFor="position">Primary Position</FormLabel>
              <FormSelect
                id="position"
                value={formData.position}
                onChange={(e) => setFormData((prev) => ({ ...prev, position: e.target.value }))}
              >
                {positions.map((pos) => (
                  <option key={pos} value={pos}>{pos}</option>
                ))}
              </FormSelect>
            </div>

            <div>
              <FormLabel htmlFor="secondary_position">Secondary Position</FormLabel>
              <FormSelect
                id="secondary_position"
                value={formData.secondary_position}
                onChange={(e) => setFormData((prev) => ({ ...prev, secondary_position: e.target.value }))}
              >
                <option value="None">None</option>
                {positions.map((pos) => (
                  <option key={pos} value={pos}>{pos}</option>
                ))}
              </FormSelect>
            </div>

            <div>
              <FormLabel htmlFor="preferred_foot">Preferred Foot</FormLabel>
              <FormSelect
                id="preferred_foot"
                value={formData.preferred_foot}
                onChange={(e) => setFormData((prev) => ({ ...prev, preferred_foot: e.target.value }))}
              >
                <option value="Right">Right</option>
                <option value="Left">Left</option>
                <option value="Both">Both</option>
              </FormSelect>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 2 — Team & Competition */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold text-white">Team & Competition</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FormLabel htmlFor="club_name">
                Club / Team Name{' '}
                <span className="text-muted-foreground normal-case font-normal">(optional)</span>
              </FormLabel>
              <Input
                id="club_name"
                type="text"
                placeholder="e.g. FC Dallas, Jefferson High School"
                value={(formData.club_name as string) ?? ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, club_name: e.target.value }))}
                className="bg-secondary/20 border-border/50 text-sm h-8"
              />
            </div>
            <div>
              <FormLabel htmlFor="grad_year">Graduation Year</FormLabel>
              <FormSelect
                id="grad_year"
                value={formData.grad_year ?? currentYear + 3}
                onChange={(e) => setFormData((prev) => ({ ...prev, grad_year: parseInt(e.target.value) }))}
              >
                {gradYears.map((y) => (
                  <option key={y} value={y}>Class of {y}</option>
                ))}
              </FormSelect>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FormLabel htmlFor="edit_level">Current Playing Level</FormLabel>
              <FormSelect
                id="edit_level"
                value={formData.level}
                onChange={(e) => setFormData((prev) => ({ ...prev, level: e.target.value, league: '' }))}
              >
                {levels.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </FormSelect>
            </div>
            <div>
              <FormLabel htmlFor="league">
                League / Competition{' '}
                <span className="text-muted-foreground normal-case font-normal">(optional)</span>
              </FormLabel>
              <FormSelect
                id="league"
                value={(formData.league as string) ?? ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, league: e.target.value }))}
              >
                <option value="">Select league…</option>
                {(leaguesByLevel[formData.level as string] ?? []).map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </FormSelect>
            </div>
          </div>

          <div>
            <FormLabel>
              Game Days{' '}
              <span className="text-muted-foreground normal-case font-normal">(optional — training plan avoids these days)</span>
            </FormLabel>
            <div className="flex gap-2 mt-1">
              {DAY_LABELS.map((label, idx) => {
                const isSelected = (formData.game_days as number[] ?? []).includes(idx);
                return (
                  <button
                    key={label}
                    type="button"
                    onClick={() => setFormData((prev) => {
                      const days = (prev.game_days as number[]) ?? [];
                      return {
                        ...prev,
                        game_days: isSelected ? days.filter((d) => d !== idx) : [...days, idx],
                      };
                    })}
                    className={cn(
                      'flex-1 h-9 text-xs font-bold rounded-lg border transition-all duration-150',
                      isSelected
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground'
                    )}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
            {(formData.game_days as number[] ?? []).length > 0 && (
              <p className="text-[10px] text-muted-foreground mt-1.5">
                Sessions scheduled away from game days and the following recovery day.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Section 3 — Development Goals */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold text-white">Development Goals</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <FormLabel htmlFor="target_level">Target Level</FormLabel>
            <FormSelect
              id="target_level"
              value={formData.target_level}
              onChange={(e) => setFormData((prev) => ({ ...prev, target_level: e.target.value }))}
            >
              {targetLevels.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </FormSelect>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FormLabel htmlFor="sessions_per_week">Sessions Per Week</FormLabel>
              <FormSelect
                id="sessions_per_week"
                value={formData.sessions_per_week}
                onChange={(e) => setFormData((prev) => ({ ...prev, sessions_per_week: parseInt(e.target.value) || 3 }))}
              >
                {[2, 3, 4, 5, 6].map((n) => (
                  <option key={n} value={n}>{n} sessions</option>
                ))}
              </FormSelect>
            </div>

            <div>
              <FormLabel htmlFor="session_duration">Session Duration</FormLabel>
              <FormSelect
                id="session_duration"
                value={formData.session_duration}
                onChange={(e) => setFormData((prev) => ({ ...prev, session_duration: parseInt(e.target.value) || 30 }))}
              >
                {[20, 30, 45, 60, 75, 90].map((d) => (
                  <option key={d} value={d}>{d} minutes</option>
                ))}
              </FormSelect>
            </div>
          </div>
        </CardContent>
      </Card>
 
      {/* Section 3 — Academic Profile */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-bold text-white">Academic Profile</CardTitle>
            <span className="text-[10px] text-muted-foreground font-medium">
              Used in recruiting emails
            </span>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            College coaches care about academics. Adding your GPA and test scores improves your AI-drafted recruiting emails — they'll be included automatically when present.
          </p>

          {/* GPA row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FormLabel htmlFor="gpa">GPA</FormLabel>
              <Input
                id="gpa"
                type="number"
                step="0.01"
                min="0"
                max="5"
                placeholder="e.g. 3.8"
                value={formData.gpa ?? ''}
                onChange={e => setFormData(prev => ({
                  ...prev,
                  gpa: e.target.value ? parseFloat(e.target.value) : undefined,
                }))}
                className="bg-secondary/20 border-border/50 text-sm h-8"
              />
            </div>
            <div>
              <FormLabel htmlFor="gpa_scale">GPA Scale</FormLabel>
              <FormSelect
                id="gpa_scale"
                value={formData.gpa_scale ?? '4.0'}
                onChange={e => setFormData(prev => ({ ...prev, gpa_scale: e.target.value }))}
              >
                <option value="4.0">4.0 Unweighted</option>
                <option value="5.0 weighted">5.0 Weighted</option>
              </FormSelect>
            </div>
          </div>

          {/* Test scores row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FormLabel htmlFor="act_score">
                ACT Score{' '}
                <span className="text-muted-foreground normal-case font-normal">(optional)</span>
              </FormLabel>
              <Input
                id="act_score"
                type="number"
                min="1"
                max="36"
                placeholder="e.g. 29"
                value={formData.act_score ?? ''}
                onChange={e => setFormData(prev => ({
                  ...prev,
                  act_score: e.target.value ? parseInt(e.target.value) : undefined,
                }))}
                className="bg-secondary/20 border-border/50 text-sm h-8"
              />
            </div>
            <div>
              <FormLabel htmlFor="sat_score">
                SAT Score{' '}
                <span className="text-muted-foreground normal-case font-normal">(optional)</span>
              </FormLabel>
              <Input
                id="sat_score"
                type="number"
                min="400"
                max="1600"
                placeholder="e.g. 1280"
                value={formData.sat_score ?? ''}
                onChange={e => setFormData(prev => ({
                  ...prev,
                  sat_score: e.target.value ? parseInt(e.target.value) : undefined,
                }))}
                className="bg-secondary/20 border-border/50 text-sm h-8"
              />
            </div>
          </div>
        </CardContent>
      </Card>
 
      {/* Section 4 — Focus & Equipment */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <CardTitle className="text-base font-bold text-white">Focus & Equipment</CardTitle>
            <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
              {(formData.focus_areas || []).length} / 3 Focus Selected
            </span>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Focus Areas */}
          <div>
            <FormLabel>Focus Areas</FormLabel>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-1.5">
              {focusOptions.map((area) => {
                const isSelected = (formData.focus_areas || []).includes(area);
                const isMaxSelected = (formData.focus_areas || []).length >= 3;
                return (
                  <button
                    key={area}
                    type="button"
                    disabled={!isSelected && isMaxSelected}
                    onClick={() => handleFocusClick(area)}
                    className={cn(
                      'w-full h-8 text-[11px] font-semibold rounded-full border transition-all duration-150 truncate disabled:opacity-30 disabled:cursor-not-allowed',
                      isSelected
                        ? 'bg-primary text-primary-foreground border-primary hover:bg-primary/95'
                        : 'bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground'
                    )}
                  >
                    {area}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Equipment */}
          <div>
            <FormLabel>Available Equipment</FormLabel>
            <div className="flex flex-wrap gap-2 mt-1.5">
              {equipmentOptions.map((eq) => {
                const isSelected = (formData.equipment_available || []).includes(eq);
                return (
                  <button
                    key={eq}
                    type="button"
                    onClick={() => handleEquipmentClick(eq)}
                    className={cn(
                      'h-8 text-[11px] font-semibold py-1.5 px-4 rounded-full border transition-all duration-150',
                      isSelected
                        ? 'bg-primary text-primary-foreground border-primary hover:bg-primary/95'
                        : 'bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground'
                    )}
                  >
                    {eq}
                  </button>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Global Error Display */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive text-xs rounded-lg font-medium text-center">
          {error}
        </div>
      )}

      {/* Save Button */}
      <div className="space-y-2">
        <Button
          type="submit"
          disabled={saving || saved}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold h-10 rounded-xl"
        >
          {saving ? 'Saving...' : saved ? '✓ Profile updated!' : 'Save Changes'}
        </Button>
        {planAffected && !saved && !saving && (
          <p className="text-[10px] text-muted-foreground/80 text-center">
            ⚡ Saving will offer to regenerate your training plan
          </p>
        )}
      </div>

      {/* Regeneration Confirm Modal */}
      {showRegenConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-card border border-border/80 rounded-xl max-w-sm w-full p-6 relative flex flex-col space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-foreground">Update Training Plan?</h2>
              <p className="text-xs text-muted-foreground leading-relaxed">
                You changed fields that affect your training plan (position, focus areas, equipment, or schedule).
                Would you like to regenerate your plan with the new settings? This will replace your current week with a freshly generated one.
              </p>
            </div>

            <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 rounded-lg p-3 text-xs leading-relaxed text-left">
              <strong>Please Note</strong>
              <p className="mt-0.5 text-yellow-500/90">
                Your completion history will be preserved but your current week's sessions will be replaced.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <Button
                type="button"
                onClick={() => saveProfile(true)}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs h-9"
              >
                Yes, regenerate my plan
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => saveProfile(false)}
                className="w-full border-border/80 hover:bg-secondary/40 text-foreground font-semibold text-xs h-9"
              >
                Save without regenerating
              </Button>
              <button
                type="button"
                onClick={() => setShowRegenConfirm(false)}
                className="text-[11px] text-muted-foreground hover:text-foreground underline transition-colors pt-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
}
