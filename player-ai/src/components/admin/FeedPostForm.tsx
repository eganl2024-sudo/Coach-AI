'use client';

import { useState } from 'react';
import { createFeedPostAction } from '@/lib/actions/admin';
import { PRESENTER_MAP } from '@/lib/data/presenters';

const POSITION_OPTIONS = [
  'Goalkeeper', 'Center Back', 'Full Back',
  'Defensive Midfielder', 'Central Midfielder',
  'Attacking Midfielder', 'Winger', 'Striker',
];

export default function FeedPostForm() {
  const [open, setOpen]               = useState(false);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState('');
  const [success, setSuccess]         = useState(false);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);

  const [form, setForm] = useState({
    presenter_id: 'KC-01',
    title: '',
    description: '',
    body: '',
    video_url: '',
    tags: '',
    coming_soon: false,
  });

  function togglePosition(pos: string) {
    setSelectedPositions(prev =>
      prev.includes(pos) ? prev.filter(p => p !== pos) : [...prev, pos]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    const result = await createFeedPostAction({
      ...form,
      position_tags: selectedPositions.join('|'),
    });
    setLoading(false);
    if (result.success) {
      setSuccess(true);
      setForm({ presenter_id: 'KC-01', title: '', description: '', body: '', video_url: '', tags: '', coming_soon: false });
      setSelectedPositions([]);
      setTimeout(() => { setSuccess(false); setOpen(false); }, 1500);
    } else {
      setError(result.error ?? 'Failed to create post.');
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="h-9 px-4 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold transition-colors cursor-pointer"
      >
        + New Post
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="border border-border/50 rounded-xl bg-card/40 p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-white">New Feed Post</h2>
        <button type="button" onClick={() => setOpen(false)} className="text-muted-foreground hover:text-white text-sm cursor-pointer">
          Cancel
        </button>
      </div>

      {/* Presenter */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Author</label>
        <select
          value={form.presenter_id}
          onChange={e => setForm(f => ({ ...f, presenter_id: e.target.value }))}
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
        >
          {Object.entries(PRESENTER_MAP).map(([id, p]) => (
            <option key={id} value={id}>{p.name} — {p.team}</option>
          ))}
        </select>
      </div>

      {/* Title */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Title *</label>
        <input
          type="text"
          value={form.title}
          onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          placeholder="e.g. What College Coaches Actually Look For in a Winger"
          required
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
      </div>

      {/* Description */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Preview / Description *</label>
        <textarea
          value={form.description}
          onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          rows={3}
          placeholder="One paragraph shown on the feed card before the player expands the post"
          required
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
        />
      </div>

      {/* Body */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Full Post Body</label>
        <textarea
          value={form.body}
          onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
          rows={8}
          placeholder="Full article content. Leave blank to show description only."
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
        />
      </div>

      {/* Video URL */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">YouTube Embed URL</label>
        <input
          type="url"
          value={form.video_url}
          onChange={e => setForm(f => ({ ...f, video_url: e.target.value }))}
          placeholder="https://www.youtube.com/embed/VIDEO_ID"
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
      </div>

      {/* Tags */}
      <div className="space-y-1.5">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Tags (pipe-separated)</label>
        <input
          type="text"
          value={form.tags}
          onChange={e => setForm(f => ({ ...f, tags: e.target.value }))}
          placeholder="e.g. defending|1v1|college soccer|recruiting"
          className="w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
      </div>

      {/* Position tags */}
      <div className="space-y-2">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Relevant Positions</label>
        <div className="flex flex-wrap gap-2">
          {POSITION_OPTIONS.map(pos => (
            <button
              key={pos}
              type="button"
              onClick={() => togglePosition(pos)}
              className={[
                'px-3 py-1 rounded-full text-xs font-semibold border transition-colors cursor-pointer',
                selectedPositions.includes(pos)
                  ? 'bg-primary/15 text-primary border-primary/30'
                  : 'bg-secondary/20 text-muted-foreground border-border/40 hover:text-white',
              ].join(' ')}
            >
              {pos}
            </button>
          ))}
        </div>
      </div>

      {/* Coming soon */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={form.coming_soon}
          onChange={e => setForm(f => ({ ...f, coming_soon: e.target.checked }))}
          className="rounded border-border/50 text-primary"
        />
        <span className="text-xs text-muted-foreground">Mark as Coming Soon (teaser only, no full content shown)</span>
      </label>

      {error && <p className="text-destructive text-xs">{error}</p>}
      {success && <p className="text-primary text-xs font-semibold">Post published!</p>}

      <div className="flex gap-3 pt-1">
        <button
          type="submit"
          disabled={loading}
          className="h-9 px-5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold transition-colors disabled:opacity-60 cursor-pointer"
        >
          {loading ? 'Publishing...' : 'Publish Post'}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="h-9 px-4 rounded-lg bg-secondary/40 hover:bg-secondary/60 text-muted-foreground text-xs font-semibold transition-colors cursor-pointer"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
