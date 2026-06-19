import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { getAllDrills } from '@/lib/data/getDrills';
import { DrillFilters } from '@/components/drills/DrillFilters';

export const metadata = {
  title: 'Drill Library',
};

export default async function DrillsIndexPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  const drills = await getAllDrills();
  const drillCount = drills.length;
  const categoryCount = new Set(drills.map((d) => d.category).filter(Boolean)).size;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-black tracking-tight text-white">Drill Library</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {drillCount} drills across {categoryCount} categories
        </p>
      </div>

      {/* Interactive Filter Grid */}
      <DrillFilters drills={drills} />
    </div>
  );
}
