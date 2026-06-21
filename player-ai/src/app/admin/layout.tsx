import Link from 'next/link';
import { getAdminSession } from '@/lib/admin';
import AdminLogoutButton from '@/components/admin/AdminLogoutButton';

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const isAdmin = await getAdminSession();

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-background">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="h-14 bg-card border-b border-border/50 px-6 flex items-center justify-between z-10 select-none shrink-0">
        <div className="flex items-center gap-6">
          <span className="text-sm font-black text-white tracking-wide">
            PLAYER AI ADMIN
          </span>
          <nav className="flex items-center gap-1">
            <Link
              href="/admin"
              className="px-3 py-1.5 rounded-md text-xs font-semibold text-muted-foreground hover:text-white hover:bg-secondary/60 transition-colors"
            >
              Drills
            </Link>
            <Link
              href="/admin/reels"
              className="px-3 py-1.5 rounded-md text-xs font-semibold text-muted-foreground hover:text-white hover:bg-secondary/60 transition-colors"
            >
              Reel Reviews
            </Link>
          </nav>
        </div>
        <AdminLogoutButton />
      </header>

      <main className="flex-1 p-6 max-w-6xl w-full mx-auto overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
