import { getAdminSession } from '@/lib/admin';
import AdminLogoutButton from '@/components/admin/AdminLogoutButton';

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const isAdmin = await getAdminSession();

  // If not authenticated, render children without the admin chrome
  // The individual pages handle their own redirect to /admin/login
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-background">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Nav Bar */}
      <header className="h-14 bg-card border-b border-border/50 px-6 flex items-center justify-between z-10 select-none shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-black text-white tracking-wide">
            ⚙️ PLAYER AI ADMIN
          </span>
        </div>
        <AdminLogoutButton />
      </header>

      {/* Main Content */}
      <main className="flex-1 p-6 max-w-6xl w-full mx-auto overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
