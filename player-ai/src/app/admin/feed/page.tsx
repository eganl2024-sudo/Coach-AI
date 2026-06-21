import { redirect } from 'next/navigation';
import { getAdminSession } from '@/lib/admin';
import { getDynamicFeedPosts } from '@/lib/actions/admin';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { SEED_POSTS } from '@/lib/data/feedPosts';
import FeedPostForm from '@/components/admin/FeedPostForm';
import FeedPostDeleteButton from '@/components/admin/FeedPostDeleteButton';

export const metadata = { title: 'Mentor Feed — Admin' };

export default async function AdminFeedPage() {
  const isAdmin = await getAdminSession();
  if (!isAdmin) redirect('/admin/login');

  const dynamicPosts = await getDynamicFeedPosts();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Mentor Feed</h1>
          <p className="text-xs text-muted-foreground mt-1">
            <span className="text-primary font-medium">{dynamicPosts.length} published</span>
            <span className="text-border/60"> · </span>
            <span>{SEED_POSTS.length} seed posts (read-only)</span>
          </p>
        </div>
        <FeedPostForm />
      </div>

      {/* Dynamic posts */}
      {dynamicPosts.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Published Posts</h2>
          <div className="border border-border/50 rounded-xl bg-card/40 overflow-hidden divide-y divide-border/20">
            {dynamicPosts.map(post => {
              const presenter = PRESENTER_MAP[post.presenter_id];
              return (
                <div key={post.post_id} className="flex items-start justify-between gap-4 px-5 py-4">
                  <div className="min-w-0 space-y-0.5">
                    <p className="text-sm font-semibold text-white truncate">{post.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {presenter?.name ?? post.presenter_id} · {post.date_posted}
                      {post.coming_soon && <span className="ml-2 text-yellow-400 font-semibold">· Coming Soon</span>}
                    </p>
                  </div>
                  <FeedPostDeleteButton postId={post.post_id} />
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Seed posts (read-only reference) */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-muted-foreground uppercase tracking-wider">
          Seed Posts (built-in, cannot be edited here)
        </h2>
        <div className="border border-border/30 rounded-xl bg-card/20 overflow-hidden divide-y divide-border/10">
          {SEED_POSTS.map(post => {
            const presenter = PRESENTER_MAP[post.presenter_id];
            return (
              <div key={post.post_id} className="flex items-start gap-4 px-5 py-3.5">
                <div className="min-w-0 space-y-0.5">
                  <p className="text-sm font-medium text-muted-foreground truncate">{post.title}</p>
                  <p className="text-xs text-muted-foreground/60">
                    {presenter?.name ?? post.presenter_id} · {post.date_posted}
                    {post.coming_soon && <span className="ml-2 text-yellow-500/70">· Coming Soon</span>}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
