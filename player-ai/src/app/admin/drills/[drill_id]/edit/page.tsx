import React from 'react';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getAdminSession } from '@/lib/admin';
import { getDrillById } from '@/lib/data/getDrills';
import DrillEditForm from '@/components/admin/DrillEditForm';

interface EditPageProps {
  params: Promise<{ drill_id: string }>;
}

export default async function AdminEditDrillPage({ params }: EditPageProps) {
  const isAdmin = await getAdminSession();
  if (!isAdmin) redirect('/admin/login');

  const { drill_id } = await params;
  const drill = await getDrillById(drill_id);

  if (!drill) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16 space-y-4">
        <h2 className="text-xl font-bold text-white">Drill not found</h2>
        <Link href="/admin" className="text-primary hover:underline text-sm font-semibold">
          ← Back to Admin Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/admin" className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors">
          ← Back to Admin Dashboard
        </Link>
        <h1 className="text-2xl font-black text-white tracking-tight mt-2">
          Edit Drill: {drill.drill_name}
        </h1>
      </div>
      <DrillEditForm drill={drill} />
    </div>
  );
}
