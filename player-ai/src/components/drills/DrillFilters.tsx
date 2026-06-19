'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CATEGORY_COLORS, DIFFICULTY_COLORS, INTENSITY_COLORS } from '@/lib/data/categories';
import type { Drill } from '@/lib/types/player';

interface DrillFiltersProps {
  drills: Drill[];
  initialCategory?: string;
}

export function DrillFilters({ drills, initialCategory = 'All' }: DrillFiltersProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [selectedIntensity, setSelectedIntensity] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filterTabs = ['All', 'Warmup', 'Technical', 'Tactical', 'Physical', 'Game Application', 'Cool Down'];

  const intensityOptions = ['All', ...Array.from(new Set(drills.map(d => d.intensity).filter(Boolean))).sort()];

  const filteredDrills = drills
    .filter(d => selectedCategory === 'All' || d.category?.toLowerCase() === selectedCategory.toLowerCase())
    .filter(d => selectedIntensity === 'All' || d.intensity === selectedIntensity)
    .filter(d => {
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        d.drill_name?.toLowerCase().includes(q) ||
        d.category?.toLowerCase().includes(q) ||
        d.description?.toLowerCase().includes(q)
      );
    });

  return (
    <div className="space-y-6">
      {/* 1. Text Search Input */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search drills..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full h-9 rounded-lg border border-border/50 bg-secondary/20 pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20"
        />
        <svg
          className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
      </div>

      {/* 2. Intensity Filter Row */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider shrink-0">
          Intensity:
        </span>
        {intensityOptions.map(opt => (
          <button
            key={opt}
            onClick={() => setSelectedIntensity(opt)}
            className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all cursor-pointer ${
              selectedIntensity === opt
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-secondary/40 text-muted-foreground border-border/40 hover:bg-secondary/70 hover:text-foreground'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>

      {/* 3. Category Filter Tabs */}
      <div className="flex flex-wrap gap-2 pb-2 border-b border-border/30">
        {filterTabs.map((tab) => {
          const isActive = selectedCategory.toLowerCase() === tab.toLowerCase();
          return (
            <Button
              key={tab}
              variant="outline"
              size="sm"
              onClick={() => setSelectedCategory(tab)}
              className={cn(
                "rounded-full transition-all text-xs font-semibold px-4 cursor-pointer",
                isActive
                  ? "bg-primary/15 text-primary border-primary hover:bg-primary/25 hover:text-primary"
                  : "border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              {tab}
            </Button>
          );
        })}
      </div>

      {/* 4. Results Count */}
      {(searchQuery || selectedCategory !== 'All' || selectedIntensity !== 'All') && (
        <p className="text-xs text-muted-foreground">
          {filteredDrills.length} {filteredDrills.length === 1 ? 'drill' : 'drills'} found
        </p>
      )}

      {/* 5. Drill Grid / Empty State */}
      {filteredDrills.length === 0 ? (
        <div className="text-center py-16 space-y-2">
          <p className="text-foreground font-semibold">No drills found</p>
          <p className="text-muted-foreground text-sm">
            Try adjusting your search or filters.
          </p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('All'); setSelectedIntensity('All'); }}
            className="text-primary text-sm font-semibold hover:underline mt-1 cursor-pointer"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDrills.map((drill) => {
            const catColor = CATEGORY_COLORS[drill.category] || 'bg-secondary text-muted-foreground border-border';
            const diffColor = DIFFICULTY_COLORS[drill.difficulty?.toLowerCase()] || 'bg-secondary text-muted-foreground';
            const hasVideo = drill.video_url && drill.video_url.trim().length > 0;
            
            // Intensity dot color
            const intensityDot = INTENSITY_COLORS[drill.intensity?.toLowerCase()] || 'bg-green-500';

            return (
              <Link
                key={drill.drill_id}
                href={`/drills/${drill.drill_id}`}
                className="group block"
              >
                <Card className="h-full border border-border/50 bg-card/40 hover:bg-card/75 backdrop-blur-sm transition-all duration-200 hover:border-primary/50 flex flex-col justify-between overflow-hidden">
                  <CardContent className="p-4 flex-1 flex flex-col justify-between space-y-4">
                    {/* Top Row: Category + Intensity dot */}
                    <div className="flex items-center justify-between">
                      <Badge className={cn("text-[10px] font-semibold border", catColor)}>
                        {drill.category}
                      </Badge>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-muted-foreground capitalize">
                          {drill.intensity}
                        </span>
                        <span className={cn("w-2 h-2 rounded-full", intensityDot)} />
                      </div>
                    </div>

                    {/* Middle: Title & Description */}
                    <div className="space-y-1.5 flex-1">
                      <h3 className="font-bold text-foreground text-base tracking-tight truncate group-hover:text-primary transition-colors">
                        {drill.drill_name}
                      </h3>
                      <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                        {drill.description}
                      </p>
                    </div>

                    {/* Bottom Row */}
                    <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-border/30">
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0 font-medium">
                        {drill.duration_minutes} min
                      </Badge>
                      <Badge variant="secondary" className={cn("text-[10px] px-1.5 py-0 font-medium border-transparent", diffColor)}>
                        {drill.difficulty}
                      </Badge>
                      {drill.min_equipment && (
                        <span className="text-[10px] text-muted-foreground truncate max-w-[100px]" title={drill.min_equipment}>
                          🔧 {drill.min_equipment}
                        </span>
                      )}
                      {hasVideo && (
                        <Badge className="text-primary bg-primary/10 border-transparent text-[10px] px-1.5 py-0 font-semibold ml-auto flex items-center gap-1">
                          ▶ Video
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
