import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { MentorFeedClient } from '@/components/feed/MentorFeedClient';
import type { FeedPost } from '@/lib/types/feed';
import { SEED_POSTS } from '@/lib/data/feedPosts';
import { getDynamicFeedPosts } from '@/lib/actions/admin';
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

  const [profile, dynamicPosts] = await Promise.all([
    getUserData<AthleteProfile>(username, 'athlete_profile'),
    getDynamicFeedPosts(),
  ]);
  const playerPosition = profile?.position ?? '';

  // Dynamic posts first (newest), then seed posts
  const allPosts: FeedPost[] = [
    ...dynamicPosts,
    ...SEED_POSTS.filter(s => !dynamicPosts.some(d => d.post_id === s.post_id)),
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-black tracking-tight text-white">Mentor Feed</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Insights and advice from professional and college athletes.
        </p>
      </div>

      {/* Feed Filter and List Client View */}
      <MentorFeedClient
        posts={allPosts}
        presenterMap={PRESENTER_MAP}
        playerPosition={playerPosition}
      />
    </div>
  );
}
