'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { saveOnboardingAction, type OnboardingFormData } from '@/lib/actions/onboarding';

function FormLabel({ children, className, htmlFor }: { children: React.ReactNode; className?: string; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className={cn("text-xs font-semibold text-muted-foreground tracking-wide uppercase block mb-1.5", className)}>
      {children}
    </label>
  );
}

function FormSelect({ className, children, ...props }: React.ComponentProps<"select">) {
  return (
    <div className="relative w-full">
      <select
        className={cn(
          "h-8 w-full rounded-lg border border-input bg-card/50 px-2.5 py-1 text-sm outline-none transition-all focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20 disabled:pointer-events-none disabled:opacity-50 text-foreground cursor-pointer appearance-none pr-8",
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

export function OnboardingForm() {
  const router = useRouter();
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<OnboardingFormData>({
    name: '',
    age: 15,
    email: '',
    position: 'Central Midfielder',
    secondary_position: 'None',
    preferred_foot: 'Right',
    age_group: 'U15',
    level: 'Competitive Club',
    league: '',
    club_name: '',
    grad_year: new Date().getFullYear() + 3,
    game_days: [],
    target_level: 'Academy/Select',
    focus_areas: [],
    equipment_available: ['Ball only'],
    sessions_per_week: 3,
    session_duration: 30,
  });

  // Pre-populate email and name from query parameters if present
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const searchParams = new URLSearchParams(window.location.search);
      const emailParam = searchParams.get('email');
      const nameParam = searchParams.get('name');
      if (emailParam || nameParam) {
        setFormData(prev => ({
          ...prev,
          email: prev.email || emailParam || '',
          name: prev.name || nameParam || '',
        }));
      }
    }
  }, []);

  // Keep age_group derived whenever age changes
  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      age_group: deriveAgeGroup(prev.age)
    }));
  }, [formData.age]);

  const validateStep = (currentStep: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (currentStep === 1) {
      if (!formData.name.trim()) {
        newErrors.name = 'Name is required.';
      }
      if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email address.';
      }
      if (!formData.age || formData.age < 10 || formData.age > 22) {
        newErrors.age = 'Age must be between 10 and 22.';
      }
      if (!formData.position) {
        newErrors.position = 'Primary position is required.';
      }
    } else if (currentStep === 2) {
      if (!formData.level) {
        newErrors.level = 'Current level is required.';
      }
      if (!formData.target_level) {
        newErrors.target_level = 'Target level is required.';
      }
      if (formData.focus_areas.length < 1) {
        newErrors.focus_areas = 'Select at least 1 focus area.';
      }
      if (formData.focus_areas.length > 3) {
        newErrors.focus_areas = 'You can select up to 3 focus areas.';
      }
    } else if (currentStep === 3) {
      if (formData.equipment_available.length < 1) {
        newErrors.equipment_available = 'At least one equipment resource is required.';
      }
      if (!formData.sessions_per_week) {
        newErrors.sessions_per_week = 'Sessions per week is required.';
      }
      if (!formData.session_duration) {
        newErrors.session_duration = 'Session duration is required.';
      }
    }

    setValidationErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      if (step < 5) {
        setStep(step + 1);
        setError('');
      } else {
        handleSubmit();
      }
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
      setValidationErrors({});
      setError('');
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await saveOnboardingAction(formData);
      if (res.success) {
        router.push('/');
      } else {
        setError(res.error || 'Failed to generate training plan.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
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

  const leaguesByLevel: Record<string, string[]> = {
    'Recreational':       ['Recreation League', 'Intramural', 'Other'],
    'Competitive Club':   ['ECNL', 'ECNL Regional', 'MLS Next', 'Girls Academy', 'State Cup', 'Regional League', 'Other'],
    'Academy/Select':     ['ECNL', 'ECNL Regional', 'MLS Next', 'Girls Academy', 'State Cup', 'Other'],
    'Varsity High School':['State Ranked', 'Varsity', 'Other'],
    'College':            ['NCAA D1', 'NCAA D2', 'NCAA D3', 'NAIA', 'NJCAA', 'Other'],
    'Professional':       ['MLS', 'MLS Next Pro', 'USL Championship', 'USL1', 'USL League Two', 'UPSL', 'Other'],
  };

  const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const currentYear = new Date().getFullYear();
  const gradYears = Array.from({ length: 8 }, (_, i) => currentYear + i);

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

  return (
    <Card className="max-w-lg mx-auto bg-card/60 border-border/50 backdrop-blur-md p-8 shadow-2xl relative overflow-hidden">
      {/* Top Progress Bar */}
      <div className="flex gap-2 mb-2">
        {[1, 2, 3, 4, 5].map((s) => (
          <div
            key={s}
            className={cn(
              "h-1.5 flex-1 rounded-full transition-all duration-300",
              s <= step ? "bg-primary" : "bg-secondary"
            )}
          />
        ))}
      </div>
      <p className="text-xs text-muted-foreground text-center mb-6">
        Step {step} of 5
      </p>

      <CardContent className="p-0">
        {step === 1 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-xl font-bold mb-1 text-white">Tell us about yourself</h3>
              <p className="text-sm text-muted-foreground mb-6">Let's start with the basics to customize your profile.</p>
            </div>

            <div className="space-y-4">
              <div>
                <FormLabel htmlFor="name">First Name</FormLabel>
                <Input
                  id="name"
                  type="text"
                  placeholder="Your first name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="bg-card/50 border-input h-8 px-2.5 text-sm rounded-lg"
                />
                {validationErrors.name && (
                  <p className="text-destructive text-xs mt-1.5 font-medium">{validationErrors.name}</p>
                )}
              </div>

              <div>
                <FormLabel htmlFor="email">Email Address <span className="text-muted-foreground normal-case font-normal">(optional — for weekly summary)</span></FormLabel>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="bg-card/50 border-input h-8 px-2.5 text-sm rounded-lg"
                />
                {validationErrors.email && (
                  <p className="text-destructive text-xs mt-1.5 font-medium">{validationErrors.email}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <FormLabel htmlFor="age">Age</FormLabel>
                  <Input
                    id="age"
                    type="number"
                    min="10"
                    max="22"
                    value={formData.age}
                    onChange={(e) => setFormData(prev => ({ ...prev, age: parseInt(e.target.value) || 0 }))}
                    className="bg-card/50 border-input h-8 px-2.5 text-sm rounded-lg"
                  />
                  {validationErrors.age && (
                    <p className="text-destructive text-xs mt-1.5 font-medium">{validationErrors.age}</p>
                  )}
                </div>

                <div>
                  <FormLabel htmlFor="age_group">Age Group</FormLabel>
                  <FormSelect
                    id="age_group"
                    value={formData.age_group}
                    disabled
                    onChange={() => {}}
                    className="cursor-not-allowed opacity-75"
                  >
                    {['U12', 'U13', 'U14', 'U15', 'U16', 'U17', 'U18', 'U19', 'U23', 'Senior'].map(g => (
                      <option key={g} value={g}>{g}</option>
                    ))}
                  </FormSelect>
                </div>
              </div>

              <div>
                <FormLabel htmlFor="position">Primary Position</FormLabel>
                <FormSelect
                  id="position"
                  value={formData.position}
                  onChange={(e) => setFormData(prev => ({ ...prev, position: e.target.value }))}
                >
                  {positions.map(pos => (
                    <option key={pos} value={pos}>{pos}</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="secondary_position">Secondary Position</FormLabel>
                <FormSelect
                  id="secondary_position"
                  value={formData.secondary_position}
                  onChange={(e) => setFormData(prev => ({ ...prev, secondary_position: e.target.value }))}
                >
                  <option value="None">None</option>
                  {positions.map(pos => (
                    <option key={pos} value={pos}>{pos}</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="preferred_foot">Preferred Foot</FormLabel>
                <FormSelect
                  id="preferred_foot"
                  value={formData.preferred_foot}
                  onChange={(e) => setFormData(prev => ({ ...prev, preferred_foot: e.target.value }))}
                >
                  <option value="Right">Right</option>
                  <option value="Left">Left</option>
                  <option value="Both">Both</option>
                </FormSelect>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-xl font-bold mb-1 text-white">Your team & level</h3>
              <p className="text-sm text-muted-foreground mb-6">Tell us where you play so we can calibrate your plan.</p>
            </div>

            <div className="space-y-4">
              <div>
                <FormLabel htmlFor="level">Current Playing Level</FormLabel>
                <FormSelect
                  id="level"
                  value={formData.level}
                  onChange={(e) => setFormData(prev => ({ ...prev, level: e.target.value, league: '' }))}
                >
                  {levels.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="league">League / Competition <span className="normal-case font-normal text-muted-foreground">(optional)</span></FormLabel>
                <FormSelect
                  id="league"
                  value={formData.league}
                  onChange={(e) => setFormData(prev => ({ ...prev, league: e.target.value }))}
                >
                  <option value="">Select league…</option>
                  {(leaguesByLevel[formData.level] ?? []).map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="club_name">Club / Team Name <span className="normal-case font-normal text-muted-foreground">(optional)</span></FormLabel>
                <Input
                  id="club_name"
                  type="text"
                  placeholder="e.g. FC Dallas, Jefferson High School"
                  value={formData.club_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, club_name: e.target.value }))}
                  className="bg-card/50 border-input h-8 px-2.5 text-sm rounded-lg"
                />
              </div>

              <div>
                <FormLabel htmlFor="grad_year">Graduation Year</FormLabel>
                <FormSelect
                  id="grad_year"
                  value={formData.grad_year}
                  onChange={(e) => setFormData(prev => ({ ...prev, grad_year: parseInt(e.target.value) }))}
                >
                  {gradYears.map(y => (
                    <option key={y} value={y}>Class of {y}</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="target_level">Target Playing Level</FormLabel>
                <FormSelect
                  id="target_level"
                  value={formData.target_level}
                  onChange={(e) => setFormData(prev => ({ ...prev, target_level: e.target.value }))}
                >
                  {targetLevels.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </FormSelect>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-xl font-bold mb-1 text-white">What's your current level?</h3>
              <p className="text-sm text-muted-foreground mb-6">Select up to 3 focus areas and your game days.</p>
            </div>

            <div className="space-y-5">
              <div>
                <div className="flex justify-between items-baseline mb-1">
                  <FormLabel>Focus Areas</FormLabel>
                  <span className="text-[10px] font-semibold text-muted-foreground tracking-wider uppercase">
                    {formData.focus_areas.length} / 3 Selected
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  {focusOptions.map((area) => {
                    const isSelected = formData.focus_areas.includes(area);
                    const isMaxSelected = formData.focus_areas.length >= 3;
                    return (
                      <Button
                        key={area}
                        type="button"
                        variant={isSelected ? "default" : "secondary"}
                        disabled={!isSelected && isMaxSelected}
                        onClick={() => {
                          if (isSelected) {
                            setFormData(prev => ({
                              ...prev,
                              focus_areas: prev.focus_areas.filter(a => a !== area)
                            }));
                          } else {
                            if (!isMaxSelected) {
                              setFormData(prev => ({
                                ...prev,
                                focus_areas: [...prev.focus_areas, area]
                              }));
                            }
                          }
                        }}
                        className={cn(
                          "w-full h-9 justify-center text-xs font-semibold py-2 px-3 rounded-full border transition-all duration-200 truncate cursor-pointer",
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary hover:bg-primary/90 hover:scale-[1.02]"
                            : "bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground"
                        )}
                      >
                        {area}
                      </Button>
                    );
                  })}
                </div>
                {validationErrors.focus_areas && (
                  <p className="text-destructive text-xs mt-1.5 font-medium">{validationErrors.focus_areas}</p>
                )}
              </div>

              <div>
                <FormLabel>Game Days <span className="normal-case font-normal text-muted-foreground">(optional — training plan will avoid these days)</span></FormLabel>
                <div className="flex gap-2 mt-1">
                  {DAY_LABELS.map((label, idx) => {
                    const isSelected = formData.game_days.includes(idx);
                    return (
                      <Button
                        key={label}
                        type="button"
                        variant={isSelected ? "default" : "secondary"}
                        onClick={() => setFormData(prev => ({
                          ...prev,
                          game_days: isSelected
                            ? prev.game_days.filter(d => d !== idx)
                            : [...prev.game_days, idx],
                        }))}
                        className={cn(
                          "flex-1 h-9 text-xs font-bold rounded-lg border transition-all duration-200 cursor-pointer",
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary"
                            : "bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70"
                        )}
                      >
                        {label}
                      </Button>
                    );
                  })}
                </div>
                {formData.game_days.length > 0 && (
                  <p className="text-[10px] text-muted-foreground mt-1.5">
                    Training sessions will be scheduled on non-game days with a rest day after games.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-xl font-bold mb-1 text-white">What do you have available?</h3>
              <p className="text-sm text-muted-foreground mb-6">Tell us about your equipment and training schedule.</p>
            </div>

            <div className="space-y-5">
              <div>
                <FormLabel>Equipment Available</FormLabel>
                <div className="flex flex-wrap gap-2 mt-1">
                  {equipmentOptions.map((eq) => {
                    const isSelected = formData.equipment_available.includes(eq);
                    return (
                      <Button
                        key={eq}
                        type="button"
                        variant={isSelected ? "default" : "secondary"}
                        onClick={() => {
                          if (isSelected) {
                            if (formData.equipment_available.length > 1) {
                              setFormData(prev => ({
                                ...prev,
                                equipment_available: prev.equipment_available.filter(e => e !== eq)
                              }));
                            }
                          } else {
                            setFormData(prev => ({
                              ...prev,
                              equipment_available: [...prev.equipment_available, eq]
                            }));
                          }
                        }}
                        className={cn(
                          "h-8 text-xs font-semibold py-1.5 px-3.5 rounded-full border transition-all duration-200 cursor-pointer",
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary hover:bg-primary/90"
                            : "bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground"
                        )}
                      >
                        {eq}
                      </Button>
                    );
                  })}
                </div>
                {validationErrors.equipment_available && (
                  <p className="text-destructive text-xs mt-1.5 font-medium">{validationErrors.equipment_available}</p>
                )}
              </div>

              <div>
                <FormLabel htmlFor="sessions_per_week">Weekly Sessions</FormLabel>
                <FormSelect
                  id="sessions_per_week"
                  value={formData.sessions_per_week}
                  onChange={(e) => setFormData(prev => ({ ...prev, sessions_per_week: parseInt(e.target.value) || 3 }))}
                >
                  {[2, 3, 4, 5, 6].map(n => (
                    <option key={n} value={n}>{n} sessions per week</option>
                  ))}
                </FormSelect>
              </div>

              <div>
                <FormLabel htmlFor="session_duration">Session Duration</FormLabel>
                <FormSelect
                  id="session_duration"
                  value={formData.session_duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, session_duration: parseInt(e.target.value) || 30 }))}
                >
                  {[20, 30, 45, 60, 75, 90].map(d => (
                    <option key={d} value={d}>{d} minutes</option>
                  ))}
                </FormSelect>
              </div>
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-xl font-bold mb-1 text-white">Review & confirm</h3>
              <p className="text-sm text-muted-foreground mb-6">Double check your details before we build your plan.</p>
            </div>

            <div className="bg-secondary/20 rounded-xl border border-border/40 p-5 space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4 border-b border-border/30 pb-4">
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Name</span>
                  <span className="font-semibold text-white">{formData.name}</span>
                </div>
                {formData.email && (
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Email</span>
                    <span className="font-semibold text-white">{formData.email}</span>
                  </div>
                )}
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Age & Group</span>
                  <span className="font-semibold text-white">{formData.age} ({formData.age_group})</span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Position</span>
                  <span className="font-semibold text-white">{formData.position}</span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Secondary Position</span>
                  <span className="font-semibold text-white">{formData.secondary_position}</span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Preferred Foot</span>
                  <span className="font-semibold text-white">{formData.preferred_foot} Foot</span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Playing Levels</span>
                  <span className="font-semibold text-white truncate block" title={`${formData.level} → ${formData.target_level}`}>
                    {formData.level} → {formData.target_level}
                  </span>
                </div>
                {formData.club_name && (
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Club / Team</span>
                    <span className="font-semibold text-white">{formData.club_name}</span>
                  </div>
                )}
                {formData.league && (
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">League</span>
                    <span className="font-semibold text-white">{formData.league}</span>
                  </div>
                )}
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Graduation Year</span>
                  <span className="font-semibold text-white">Class of {formData.grad_year}</span>
                </div>
                {formData.game_days.length > 0 && (
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-0.5">Game Days</span>
                    <span className="font-semibold text-white">{formData.game_days.map(d => DAY_LABELS[d]).join(', ')}</span>
                  </div>
                )}
              </div>

              <div>
                <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-1.5">Focus Areas</span>
                <div className="flex flex-wrap gap-1.5">
                  {formData.focus_areas.map(fa => (
                    <span key={fa} className="text-xs font-semibold px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full">
                      {fa}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block mb-1.5">Equipment Available</span>
                <div className="flex flex-wrap gap-1.5">
                  {formData.equipment_available.map(eq => (
                    <span key={eq} className="text-xs font-semibold px-3 py-1 bg-secondary text-secondary-foreground border border-border/50 rounded-full">
                      {eq}
                    </span>
                  ))}
                </div>
              </div>

              <div className="border-t border-border/30 pt-4 flex justify-between items-center">
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block">Weekly Schedule</span>
                  <span className="text-sm font-bold text-white">
                    {formData.sessions_per_week} Sessions / Week
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold block">Session Duration</span>
                  <span className="text-sm font-bold text-white">
                    {formData.session_duration} min each
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 text-center">
              <h4 className="text-sm font-bold text-primary">Looks good!</h4>
              <p className="text-xs text-muted-foreground mt-0.5">Let's generate your customized weekly training plan.</p>
            </div>
          </div>
        )}

        {/* Global Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 text-destructive text-xs rounded-lg font-medium text-center">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 mt-8">
          {step > 1 && (
            <Button
              type="button"
              variant="outline"
              disabled={loading}
              onClick={handleBack}
              className="flex-1 h-9 rounded-lg border-border hover:bg-muted text-foreground cursor-pointer"
            >
              Back
            </Button>
          )}
          <Button
            type="button"
            disabled={loading}
            onClick={handleNext}
            className="flex-1 h-9 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-semibold cursor-pointer shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-1.5">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Generating Plan...
              </span>
            ) : step === 5 ? (
              "Generate My Plan"
            ) : (
              "Next"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
