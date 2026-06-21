'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';

const REVIEWERS = [
  { id: '',        label: 'All' },
  { id: 'KC-01',   label: 'Mitch (KC)' },
  { id: 'UNLV-01', label: 'Nick (UNLV)' },
  { id: 'TFC-01',  label: 'TFC Coach' },
  { id: 'YOU-01',  label: 'You' },
];

export default function ReelReviewFilterTabs() {
  const router     = useRouter();
  const pathname   = usePathname();
  const params     = useSearchParams();
  const current    = params.get('reviewer') ?? '';

  function select(id: string) {
    const next = new URLSearchParams(params.toString());
    if (id) next.set('reviewer', id);
    else next.delete('reviewer');
    router.replace(`${pathname}?${next.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {REVIEWERS.map(r => (
        <button
          key={r.id}
          onClick={() => select(r.id)}
          className={[
            'px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer',
            current === r.id
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary/40 text-muted-foreground hover:text-white hover:bg-secondary/70',
          ].join(' ')}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}
