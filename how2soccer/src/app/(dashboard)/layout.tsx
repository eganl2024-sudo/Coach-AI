import { redirect } from 'next/navigation'
import { getCurrentParent, getSessionKid } from '@/lib/session'
import { Header } from '@/components/layout/Header'
import { BottomNav } from '@/components/layout/BottomNav'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const parent = await getCurrentParent()
  if (!parent) redirect('/login')

  const kid = await getSessionKid()
  if (!kid) redirect('/onboarding')

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-1 pb-24 max-w-lg mx-auto w-full px-4">{children}</main>
      <BottomNav />
    </div>
  )
}
