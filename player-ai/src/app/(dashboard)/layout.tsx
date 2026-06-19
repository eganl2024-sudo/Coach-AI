import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { Sidebar } from '@/components/layout/Sidebar';
import { getUserData } from '@/lib/data/getUserData';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const username = await getCurrentUser();
  if (!username) redirect('/login');

  const profile = await getUserData<{ name: string }>(username, 'athlete_profile');
  if (!profile) redirect('/onboarding');

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar username={username} displayName={profile?.name} />
      <main className="flex-1 overflow-y-auto p-6 lg:p-8 pt-14 md:pt-6 lg:pt-8">
        {children}
      </main>
    </div>
  );
}
