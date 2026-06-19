'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { updateDrillAction } from '@/lib/actions/admin';
import type { Drill } from '@/lib/types/player';

// Styled custom Textarea matching input component
function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      className={cn(
        "w-full min-w-0 rounded-lg border border-input bg-card/30 px-2.5 py-2 text-sm text-foreground transition-all outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20 disabled:pointer-events-none disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}

// Styled custom Select matching input component
function Select({ className, children, ...props }: React.ComponentProps<"select">) {
  return (
    <div className="relative w-full">
      <select
        className={cn(
          "h-8 w-full rounded-lg border border-input bg-card/30 px-2.5 py-1 text-sm outline-none transition-all focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20 disabled:pointer-events-none disabled:opacity-50 text-foreground cursor-pointer appearance-none pr-8",
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

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
      {children}
    </label>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground/80 pb-1.5 border-b border-border/40 mb-4">
      {children}
    </h3>
  );
}

interface DrillEditFormProps {
  drill: Drill;
}

export default function DrillEditForm({ drill }: DrillEditFormProps) {
  const [formData, setFormData] = useState<Drill>({ ...drill });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  // Handle inputs updates
  const handleChange = (
    key: keyof Drill,
    value: string | number | boolean
  ) => {
    setFormData(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    setSaved(false);

    try {
      const res = await updateDrillAction(drill.drill_id, formData);
      if (res.success) {
        setSaved(true);
      } else {
        setError(res.error || 'Failed to save changes.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setSaving(false);
    }
  };

  // Reset saved status alert after 2 seconds
  useEffect(() => {
    if (saved) {
      const timer = setTimeout(() => setSaved(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [saved]);

  return (
    <form onSubmit={handleSubmit} className="space-y-6 pb-20">
      {/* Section 1 — Identity */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm p-4">
        <CardContent className="p-0 space-y-4">
          <SectionHeading>Section 1 — Identity</SectionHeading>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <FieldLabel>Drill Name</FieldLabel>
              <Input
                type="text"
                value={formData.drill_name || ''}
                onChange={e => handleChange('drill_name', e.target.value)}
                required
                className="bg-card/30"
              />
            </div>
            
            <div>
              <FieldLabel>Drill ID (Primary Key)</FieldLabel>
              <Input
                type="text"
                value={formData.drill_id || ''}
                disabled
                className="bg-secondary/40 text-muted-foreground cursor-not-allowed opacity-80"
              />
            </div>

            <div>
              <FieldLabel>Category</FieldLabel>
              <Select
                value={formData.category || 'Technical'}
                onChange={e => handleChange('category', e.target.value)}
              >
                {['Warmup', 'Technical', 'Tactical', 'Physical', 'Game Application', 'Cool Down'].map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </Select>
            </div>

            <div>
              <FieldLabel>Skill Category</FieldLabel>
              <Input
                type="text"
                value={formData.skill_category || ''}
                onChange={e => handleChange('skill_category', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Series Name</FieldLabel>
              <Input
                type="text"
                value={formData.series_name || ''}
                onChange={e => handleChange('series_name', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Series Order</FieldLabel>
              <Input
                type="number"
                value={formData.series_order ?? 0}
                onChange={e => handleChange('series_order', parseInt(e.target.value) || 0)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Status</FieldLabel>
              <Select
                value={formData.status || 'Draft'}
                onChange={e => handleChange('status', e.target.value)}
              >
                {['Published', 'Draft', 'Archived'].map(st => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </Select>
            </div>

            <div>
              <FieldLabel>Video Status</FieldLabel>
              <Select
                value={formData.video_status || 'Not Filmed'}
                onChange={e => handleChange('video_status', e.target.value)}
              >
                {['Not Filmed', 'Filmed', 'Processed'].map(vs => (
                  <option key={vs} value={vs}>{vs}</option>
                ))}
              </Select>
            </div>

            <div className="flex items-center gap-2 pt-6">
              <input
                id="beta_ready"
                type="checkbox"
                checked={!!formData.beta_ready}
                onChange={e => handleChange('beta_ready', e.target.checked)}
                className="w-4 h-4 rounded border-input bg-card/30 text-primary focus:ring-primary/20 accent-primary cursor-pointer"
              />
              <label htmlFor="beta_ready" className="text-xs font-semibold text-white cursor-pointer select-none">
                Beta Ready (Check to flag as ready)
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 2 — Content */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm p-4">
        <CardContent className="p-0 space-y-4">
          <SectionHeading>Section 2 — Content</SectionHeading>
          
          <div className="space-y-4">
            <div>
              <FieldLabel>Description</FieldLabel>
              <Textarea
                rows={4}
                value={formData.description || ''}
                onChange={e => handleChange('description', e.target.value)}
              />
            </div>

            <div>
              <FieldLabel>Setup Data</FieldLabel>
              <Textarea
                rows={3}
                value={formData.setup_data || ''}
                onChange={e => handleChange('setup_data', e.target.value)}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <FieldLabel>Equipment Description</FieldLabel>
                <Input
                  type="text"
                  value={formData.equipment || ''}
                  onChange={e => handleChange('equipment', e.target.value)}
                  className="bg-card/30"
                />
              </div>

              <div>
                <FieldLabel>Minimum Equipment Required</FieldLabel>
                <Input
                  type="text"
                  value={formData.min_equipment || ''}
                  onChange={e => handleChange('min_equipment', e.target.value)}
                  className="bg-card/30"
                />
              </div>
            </div>

            <div>
              <FieldLabel>Game Application (Why it matters)</FieldLabel>
              <Textarea
                rows={3}
                value={formData.game_application || ''}
                onChange={e => handleChange('game_application', e.target.value)}
              />
            </div>

            <div>
              <FieldLabel>Coaching Points (General)</FieldLabel>
              <Textarea
                rows={3}
                value={formData.coaching_points || ''}
                onChange={e => handleChange('coaching_points', e.target.value)}
              />
            </div>

            <div>
              <FieldLabel>Coaching Cues (Pipe-separated | )</FieldLabel>
              <Textarea
                rows={3}
                value={formData.coaching_cues || ''}
                onChange={e => handleChange('coaching_cues', e.target.value)}
                placeholder="e.g. Keep chest over ball | Lock ankle | Strike through center"
              />
            </div>

            <div>
              <FieldLabel>Common Mistakes (Pipe-separated | )</FieldLabel>
              <Textarea
                rows={3}
                value={formData.common_mistakes || ''}
                onChange={e => handleChange('common_mistakes', e.target.value)}
                placeholder="e.g. Looking down too much | Ankle loose | Back foot planting"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 3 — Parameters */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm p-4">
        <CardContent className="p-0 space-y-4">
          <SectionHeading>Section 3 — Parameters</SectionHeading>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <FieldLabel>Difficulty</FieldLabel>
              <Select
                value={formData.difficulty || 'intermediate'}
                onChange={e => handleChange('difficulty', e.target.value)}
              >
                {['beginner', 'intermediate', 'advanced', 'elite'].map(dif => (
                  <option key={dif} value={dif}>{dif}</option>
                ))}
              </Select>
            </div>

            <div>
              <FieldLabel>Intensity</FieldLabel>
              <Select
                value={formData.intensity || 'medium'}
                onChange={e => handleChange('intensity', e.target.value)}
              >
                {['low', 'medium', 'high'].map(int => (
                  <option key={int} value={int}>{int}</option>
                ))}
              </Select>
            </div>

            <div>
              <FieldLabel>Duration (Minutes)</FieldLabel>
              <Input
                type="number"
                value={formData.duration_minutes ?? 10}
                onChange={e => handleChange('duration_minutes', parseInt(e.target.value) || 0)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Players Min</FieldLabel>
              <Input
                type="number"
                value={formData.players_min ?? 1}
                onChange={e => handleChange('players_min', parseInt(e.target.value) || 0)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Players Max</FieldLabel>
              <Input
                type="number"
                value={formData.players_max ?? 2}
                onChange={e => handleChange('players_max', parseInt(e.target.value) || 0)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Space Required</FieldLabel>
              <Input
                type="text"
                value={formData.space_required || ''}
                onChange={e => handleChange('space_required', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Drill Type</FieldLabel>
              <Select
                value={formData.drill_type || 'Isolation'}
                onChange={e => handleChange('drill_type', e.target.value)}
              >
                {['Isolation', 'Pressure', 'Game Application'].map(dt => (
                  <option key={dt} value={dt}>{dt}</option>
                ))}
              </Select>
            </div>

            <div className="flex items-center gap-2 pt-6 sm:col-span-2">
              <input
                id="solo_possible"
                type="checkbox"
                checked={!!formData.solo_possible}
                onChange={e => handleChange('solo_possible', e.target.checked)}
                className="w-4 h-4 rounded border-input bg-card/30 text-primary focus:ring-primary/20 accent-primary cursor-pointer"
              />
              <label htmlFor="solo_possible" className="text-xs font-semibold text-white cursor-pointer select-none">
                Solo Possible (Check if drill can be done alone)
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 4 — Targeting */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm p-4">
        <CardContent className="p-0 space-y-4">
          <SectionHeading>Section 4 — Targeting</SectionHeading>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FieldLabel>Primary Position Match</FieldLabel>
              <Input
                type="text"
                value={formData.position_primary || ''}
                onChange={e => handleChange('position_primary', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Position Relevance (Pipe-separated | )</FieldLabel>
              <Input
                type="text"
                value={formData.position_relevance || ''}
                onChange={e => handleChange('position_relevance', e.target.value)}
                placeholder="e.g. Center Back | Defensive Midfielder"
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>RRS Benchmark</FieldLabel>
              <Input
                type="text"
                value={formData.rrs_benchmark || ''}
                onChange={e => handleChange('rrs_benchmark', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>Tags (Pipe-separated | )</FieldLabel>
              <Input
                type="text"
                value={formData.tags || ''}
                onChange={e => handleChange('tags', e.target.value)}
                placeholder="e.g. Shooting | Heading | Finishing"
                className="bg-card/30"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 5 — Media */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm p-4">
        <CardContent className="p-0 space-y-4">
          <SectionHeading>Section 5 — Media & Routing</SectionHeading>
          
          <div className="space-y-4">
            <div>
              <FieldLabel>Video YouTube URL</FieldLabel>
              <Input
                type="text"
                value={formData.video_url || ''}
                onChange={e => handleChange('video_url', e.target.value)}
                className="bg-card/30"
              />
              {formData.video_url && (
                <p className="text-xs text-primary mt-1.5 font-medium">
                  <a href={formData.video_url} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-1">
                    ▶ Test YouTube link
                  </a>
                </p>
              )}
            </div>

            <div>
              <FieldLabel>Diagram URL</FieldLabel>
              <Input
                type="text"
                value={formData.diagram_url || ''}
                onChange={e => handleChange('diagram_url', e.target.value)}
                className="bg-card/30"
              />
            </div>

            <div>
              <FieldLabel>URL Slug</FieldLabel>
              <Input
                type="text"
                value={formData.slug || ''}
                onChange={e => handleChange('slug', e.target.value)}
                className="bg-card/30"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Form Error Display */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive text-sm rounded-lg font-medium text-center">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={saving}
        className={cn(
          "w-full h-11 text-sm font-semibold rounded-lg shadow-lg transition-all cursor-pointer",
          saved
            ? "bg-emerald-500 text-white hover:bg-emerald-500/90 shadow-emerald-500/10"
            : "bg-primary text-primary-foreground hover:bg-primary/95 shadow-primary/10"
        )}
      >
        {saving ? 'Saving...' : saved ? '✓ Saved' : 'Save Changes'}
      </Button>
    </form>
  );
}
