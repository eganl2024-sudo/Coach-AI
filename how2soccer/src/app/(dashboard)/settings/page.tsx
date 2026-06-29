import type { Metadata } from 'next'
import Link from 'next/link'
import { getSession } from '@/lib/session'
import { getParentWithKids } from '@/lib/actions/settings'
import { getStreak } from '@/lib/actions/streaks'
import { logoutAction } from '@/lib/actions/auth'
import { KidSwitcher } from '@/components/settings/KidSwitcher'
import { TimezoneSelector } from '@/components/settings/TimezoneSelector'
import { Button } from '@/components/ui/button'

export const metadata: Metadata = { title: 'Settings' }

export default async function SettingsPage() {
  const session = await getSession()
  const [parentData, streak] = await Promise.all([
    getParentWithKids(session.parentId!),
    getStreak(session.kidId!),
  ])

  return (
    <div className="py-6 space-y-4">
      <h1 className="text-2xl font-black text-gray-900">Settings</h1>

      {/* Account */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5 space-y-3">
        <h2 className="font-bold text-gray-900">Account</h2>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-2xl shrink-0">
            👤
          </div>
          <div>
            <p className="font-black text-gray-900">@{parentData.username}</p>
            <p className="text-sm text-gray-400">{parentData.email}</p>
          </div>
        </div>
      </div>

      {/* Your Players */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5 space-y-3">
        <h2 className="font-bold text-gray-900">Your Players</h2>

        {parentData.kids.length === 0 ? (
          <p className="text-sm text-gray-400">No players yet.</p>
        ) : parentData.kids.length === 1 ? (
          <div className="flex items-center gap-4 rounded-2xl border-2 border-green-500 bg-green-50 p-4">
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-xl shrink-0">⚽</div>
            <div className="flex-1">
              <p className="font-bold text-gray-900">{parentData.kids[0].name}</p>
              <p className="text-xs text-gray-400 capitalize">Age {parentData.kids[0].age} · {parentData.kids[0].skill_level}</p>
            </div>
            <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">Active</span>
          </div>
        ) : (
          <KidSwitcher kids={parentData.kids} activeKidId={session.kidId!} />
        )}

        <Link
          href="/onboarding"
          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border-2 border-dashed border-gray-200 text-sm font-semibold text-gray-500 hover:border-green-400 hover:text-green-600 transition-colors"
        >
          + Add Another Player
        </Link>
      </div>

      {/* Timezone */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5 space-y-3">
        <div>
          <h2 className="font-bold text-gray-900">Timezone</h2>
          <p className="text-xs text-gray-400 mt-0.5">Used to calculate daily streaks correctly</p>
        </div>
        <TimezoneSelector currentTimezone={streak?.timezone ?? 'America/New_York'} />
      </div>

      {/* Parent Dashboard */}
      <Link
        href="/parent"
        className="flex items-center justify-between w-full bg-slate-800 text-white rounded-2xl px-5 py-4 font-bold hover:bg-slate-700 transition-colors"
      >
        <span>📊 Parent Dashboard</span>
        <span className="text-slate-400 text-sm">View progress →</span>
      </Link>

      {/* Sign out */}
      <form action={logoutAction}>
        <Button variant="outline" className="w-full border-red-200 text-red-500 hover:bg-red-50">
          Sign Out
        </Button>
      </form>
    </div>
  )
}
