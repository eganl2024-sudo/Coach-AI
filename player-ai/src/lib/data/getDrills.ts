import { unstable_cache } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import type { Drill } from '@/lib/types/player';

const getCachedDrills = unstable_cache(
  async (includeDrafts = false): Promise<Drill[]> => {
    const supabase = await createServerClient();
    let query = supabase.from('drills').select('*');

    if (!includeDrafts) {
      query = query.eq('status', 'Published');
    }

    const { data, error } = await query.order('series_order', { ascending: true });

    if (error) {
      console.error('Failed to fetch drills:', error.message);
      return [];
    }

    return (data as Drill[]) ?? [];
  },
  ['drills-list'],
  {
    revalidate: 3600, // revalidate every hour
    tags: ['drills'],
  }
);

export async function getAllDrills(includeDrafts = false): Promise<Drill[]> {
  return getCachedDrills(includeDrafts);
}

export async function getDrillById(drillId: string): Promise<Drill | null> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('drills')
      .select('*')
      .eq('drill_id', drillId)
      .single();
    if (error || !data) return null;
    return data as Drill;
  } catch {
    return null;
  }
}
