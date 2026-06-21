'use client';

import { useState } from 'react';
import { deleteFeedPostAction } from '@/lib/actions/admin';

export default function FeedPostDeleteButton({ postId }: { postId: string }) {
  const [confirming, setConfirming] = useState(false);
  const [loading, setLoading]       = useState(false);

  async function handleDelete() {
    setLoading(true);
    await deleteFeedPostAction(postId);
    setLoading(false);
  }

  if (confirming) {
    return (
      <span className="flex items-center gap-2">
        <button
          onClick={handleDelete}
          disabled={loading}
          className="text-xs font-bold text-destructive hover:underline cursor-pointer disabled:opacity-60"
        >
          {loading ? 'Deleting...' : 'Confirm delete'}
        </button>
        <button
          onClick={() => setConfirming(false)}
          className="text-xs text-muted-foreground hover:text-white cursor-pointer"
        >
          Cancel
        </button>
      </span>
    );
  }

  return (
    <button
      onClick={() => setConfirming(true)}
      className="text-xs text-muted-foreground hover:text-destructive transition-colors cursor-pointer"
    >
      Delete
    </button>
  );
}
