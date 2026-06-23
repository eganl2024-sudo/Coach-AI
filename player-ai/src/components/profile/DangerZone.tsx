'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { deleteAccountAction } from '@/lib/actions/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function DangerZone({ username }: { username: string }) {
  const router = useRouter();
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmInput, setConfirmInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleDelete() {
    if (confirmInput !== username) {
      setError('Username does not match.');
      return;
    }
    setLoading(true);
    const result = await deleteAccountAction();
    if (result.success) {
      router.push('/login');
      router.refresh();
    } else {
      setError(result.error ?? 'Failed to delete account.');
      setLoading(false);
    }
  }

  return (
    <Card className="border-destructive/30 bg-destructive/5">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-bold text-destructive">Danger Zone</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground text-left">
          Permanently delete your account and all training data. This cannot be undone.
        </p>

        {!showConfirm ? (
          <Button
            variant="destructive"
            onClick={() => setShowConfirm(true)}
            className="min-h-[44px] font-semibold cursor-pointer"
          >
            Delete My Account
          </Button>
        ) : (
          <div className="space-y-3 max-w-sm text-left">
            <div className="space-y-1.5">
              <Label htmlFor="confirmUsername" className="text-xs text-muted-foreground uppercase font-semibold">
                Type your username <span className="text-foreground font-mono font-semibold lowercase">{username}</span> to confirm
              </Label>
              <Input
                id="confirmUsername"
                type="text"
                value={confirmInput}
                onChange={e => setConfirmInput(e.target.value)}
                placeholder={username}
                className="border-destructive/40 focus-visible:ring-destructive/30 text-sm"
              />
            </div>

            {error && (
              <p className="text-sm text-destructive font-medium">{error}</p>
            )}

            <div className="flex gap-2">
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={loading || confirmInput !== username}
                className="font-semibold cursor-pointer"
              >
                {loading ? 'Deleting...' : 'Permanently Delete'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                type="button"
                onClick={() => { setShowConfirm(false); setConfirmInput(''); setError(''); }}
                className="cursor-pointer"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
