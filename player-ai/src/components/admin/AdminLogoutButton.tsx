'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { adminLogoutAction } from '@/lib/actions/admin';

export default function AdminLogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await adminLogoutAction();
      router.push('/admin/login');
      router.refresh();
    } catch {
      // Ignore errors on logout
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleLogout}
      className="text-muted-foreground hover:text-foreground cursor-pointer select-none"
    >
      Sign Out
    </Button>
  );
}
