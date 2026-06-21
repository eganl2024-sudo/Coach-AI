import { redirect } from 'next/navigation';
import { getAdminSession } from '@/lib/admin';
import { getAllSubmittedReels } from '@/lib/data/getAdminReels';
import { getSignedUrl } from '@/lib/data/getReels';
import ReelReviewCard from '@/components/admin/ReelReviewCard';

export const metadata = { title: 'Reel Review Queue' };

export default async function AdminReelsPage() {
  const isAdmin = await getAdminSession();
  if (!isAdmin) redirect('/admin/login');

  const reels = await getAllSubmittedReels();

  const signedUrlResults = await Promise.all(reels.map(r => getSignedUrl(r.clip_path)));
  const signedUrls: Record<string, string | null> = {};
  reels.forEach((r, i) => { signedUrls[r.id] = signedUrlResults[i]; });

  const pending = reels.filter(r => r.review_status === 'pending');
  const reviewed = reels.filter(r => r.review_status === 'reviewed');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Reel Review Queue</h1>
          <p className="text-xs text-muted-foreground mt-1 flex gap-x-2">
            <span className="text-yellow-400 font-medium">{pending.length} pending</span>
            <span className="text-border/60">·</span>
            <span className="text-primary font-medium">{reviewed.length} reviewed</span>
          </p>
        </div>
      </div>

      {reels.length === 0 ? (
        <div className="border border-border/50 rounded-xl bg-card/40 py-16 text-center">
          <p className="text-muted-foreground text-sm">No submissions yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reels.map(reel => (
            <ReelReviewCard
              key={reel.id}
              reel={reel}
              signedUrl={signedUrls[reel.id] ?? null}
            />
          ))}
        </div>
      )}
    </div>
  );
}
