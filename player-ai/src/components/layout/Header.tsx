import { getCurrentUser } from '@/lib/session';

export async function Header() {
  const username = await getCurrentUser();
  return (
    <header className="h-14 border-b border-border/50 flex items-center px-6 shrink-0">
      <p className="text-sm text-muted-foreground">
        Welcome back, <span className="text-foreground font-medium">{username}</span>
      </p>
    </header>
  );
}
