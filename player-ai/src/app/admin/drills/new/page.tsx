import React from 'react';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getAdminSession } from '@/lib/admin';
import DrillAddForm from '@/components/admin/DrillAddForm';

export default async function AdminAddDrillPage() {
  const isAdmin = await getAdminSession();
  if (!isAdmin) {
    redirect('/admin/login');
  }
  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/admin"
          className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors select-none"
        >
          ← Back to Admin Dashboard
        </Link>
        <h1 className="text-2xl font-black text-white tracking-tight mt-2">
          Add New Drill
        </h1>
      </div>
      <DrillAddForm />
    </div>
  );
}
