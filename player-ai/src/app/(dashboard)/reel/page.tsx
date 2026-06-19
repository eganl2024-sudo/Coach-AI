import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { getUserReels, getSignedUrl } from '@/lib/data/getReels';
import ReelUploadForm from '@/components/reel/ReelUploadForm';
import ReelGrid from '@/components/reel/ReelGrid';
import { Badge } from '@/components/ui/badge';
import { getUserData } from '@/lib/data/getUserData';
import type { AthleteProfile } from '@/lib/types/player';
import ReelGuide from '@/components/reel/ReelGuide';

export const metadata = {
  title: 'Highlight Reel',
};

export default async function ReelPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');
  const playerPosition = profile?.position ?? '';

  const POSITION_TAB_MAP: Record<string, number> = {
    'Goalkeeper': 0,
    'Center Back': 1,
    'Full Back': 2,
    'Defensive Midfielder': 3,
    'Central Midfielder': 3,
    'Attacking Midfielder': 3,
    'Winger': 4,
    'Striker': 5,
  };
  const defaultTabIndex = POSITION_TAB_MAP[playerPosition] ?? 0;

  const reels = await getUserReels(username);

  // Generate signed URLs in parallel
  const signedUrlResults = await Promise.all(
    reels.map((r) => getSignedUrl(r.clip_path))
  );

  const signedUrls: Record<string, string> = {};
  reels.forEach((r, i) => {
    if (signedUrlResults[i]) {
      signedUrls[r.id] = signedUrlResults[i]!;
    }
  });

  return (
    <div className="space-y-10 max-w-4xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight">
          🎬 Highlight Reel
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Build a reel that gets you recruited.
        </p>
      </div>

      {/* Guide — all new content */}
      <ReelGuide defaultTabIndex={defaultTabIndex} playerPosition={playerPosition} />

      {/* Divider between guide and upload */}
      <div className="border-t border-border/30 pt-8 space-y-8">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Upload Your Reel</h2>
          <p className="text-sm text-muted-foreground">
            Submit your clips for review. Our team will give you position-specific feedback.
          </p>
        </div>

        {/* Upload Section */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground tracking-tight">
            Upload a Clip
          </h2>
          <ReelUploadForm />
        </div>

        {/* Your Clips Section */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-foreground tracking-tight">
              Your Clips
            </h2>
            <Badge className="bg-secondary/50 text-muted-foreground text-xs font-semibold px-2 py-0.5 border-transparent">
              {reels.length} {reels.length === 1 ? 'clip' : 'clips'}
            </Badge>
          </div>
          <ReelGrid reels={reels} signedUrls={signedUrls} />
        </div>
      </div>
    </div>
  );
}
