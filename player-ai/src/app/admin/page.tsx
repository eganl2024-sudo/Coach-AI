import React from 'react';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getAdminSession } from '@/lib/admin';
import { getAllDrills } from '@/lib/data/getDrills';
import { CATEGORY_COLORS, DIFFICULTY_COLORS } from '@/lib/data/categories';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export default async function AdminDashboardPage() {
  const isAdmin = await getAdminSession();
  if (!isAdmin) redirect('/admin/login');

  const drills = await getAllDrills(true);

  const totalCount = drills.length;
  const publishedCount = drills.filter(
    d => (d.status || '').toLowerCase().trim() === 'published'
  ).length;
  const filmedCount = drills.filter(
    d => ['filmed', 'processed'].includes((d.video_status || '').toLowerCase().trim())
  ).length;

  return (
    <div className="space-y-6">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Drill Library</h1>
          <p className="text-xs text-muted-foreground mt-1 flex flex-wrap gap-x-2 gap-y-1">
            <span>{totalCount} drills</span>
            <span className="text-border/60">•</span>
            <span className="text-primary font-medium">{publishedCount} published</span>
            <span className="text-border/60">•</span>
            <span className="text-sky-400 font-medium">{filmedCount} filmed</span>
          </p>
        </div>
        <div className="shrink-0">
          <Link
            href="/admin/drills/new"
            className="inline-flex items-center justify-center h-9 px-4 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold transition-colors"
          >
            + Add New Drill
          </Link>
        </div>
      </div>

      {/* Drill Table */}
      <div className="border border-border/50 rounded-xl bg-card/40 overflow-hidden">
        <div className="overflow-x-auto w-full">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-card/50 border-b border-border/50 text-[10px] uppercase tracking-wider font-semibold text-muted-foreground">
                <th className="px-5 py-3.5">ID</th>
                <th className="px-5 py-3.5">Name</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5">Difficulty</th>
                <th className="px-5 py-3.5 text-center">Video</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20">
              {drills.map((drill) => {
                const catColor = CATEGORY_COLORS[drill.category] || 'bg-secondary text-muted-foreground border-border';
                const diffColor = DIFFICULTY_COLORS[drill.difficulty?.toLowerCase()] || 'bg-secondary text-muted-foreground';
                const isPublished = (drill.status || '').toLowerCase().trim() === 'published';
                const hasVideo = drill.video_url && drill.video_url.trim().length > 0;

                return (
                  <tr key={drill.drill_id} className="hover:bg-card/25 transition-colors group">
                    <td className="px-5 py-3.5 font-mono text-xs text-muted-foreground">{drill.drill_id}</td>
                    <td className="px-5 py-3.5 font-semibold text-white">{drill.drill_name}</td>
                    <td className="px-5 py-3.5">
                      <Badge className={cn("text-[10px] font-semibold border px-2 py-0.5", catColor)}>
                        {drill.category}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={cn("text-[11px] font-bold capitalize px-2.5 py-0.5 rounded-full", diffColor)}>
                        {drill.difficulty}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      {hasVideo
                        ? <span className="text-xs font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded">▶ Yes</span>
                        : <span className="text-muted-foreground/40 font-mono">—</span>
                      }
                    </td>
                    <td className="px-5 py-3.5">
                      {isPublished
                        ? <span className="text-xs text-primary font-semibold">● Published</span>
                        : <span className="text-xs text-yellow-500 font-semibold">● {drill.status || 'Draft'}</span>
                      }
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link href={`/admin/drills/${drill.drill_id}/edit`} className="text-xs font-bold text-primary hover:underline">
                        Edit
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
