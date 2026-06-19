import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { MentorFeedClient } from '@/components/feed/MentorFeedClient';
import type { FeedPost } from '@/lib/types/feed';
import { SEED_POSTS } from '@/lib/data/feedPosts';
import { getUserData } from '@/lib/data/getUserData';
import type { AthleteProfile } from '@/lib/types/player';

export const metadata = {
  title: 'Mentor Feed',
};

export default async function MentorFeedPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');
  const playerPosition = profile?.position ?? '';

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-black tracking-tight text-white animate-fade-in">Mentor Feed</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Insights and advice from professional and college athletes.
        </p>
      </div>

      {/* Feed Filter and List Client View */}
      <MentorFeedClient
        posts={SEED_POSTS}
        presenterMap={PRESENTER_MAP}
        playerPosition={playerPosition}
      />
    </div>
  );
}
