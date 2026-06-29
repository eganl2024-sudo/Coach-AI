import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { getSession } from '@/lib/session'
import { getParentDashboard } from '@/lib/actions/parent'

import { KidSummaryCard } from '@/components/parent/KidSummaryCard'

export const metadata: Metadata = { title: 'Parent Dashboard' }

export default async function ParentDashboardPage() {
  const session = await getSession()
  const kids = await getParentDashboard(session.parentId!)

  const totalStars = kids.reduce((s, k) => s + k.totalStars, 0)
  const activeDaysThisWeek = Math.max(...kids.map((k) => k.weeklyDates.length), 0)

  return (
    <div className="py-6 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Link
          href="/settings"
          className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-gray-900">Parent Dashboard</h1>
          <p className="text-xs text-gray-400">@{session.parentUsername}</p>
        </div>
      </div>

      {/* Summary strip */}
      {kids.length > 1 && (
        <div className="bg-slate-800 rounded-2xl p-4 grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xl font-black text-white">{kids.length}</p>
            <p className="text-xs text-slate-400">players</p>
          </div>
          <div>
            <p className="text-xl font-black text-yellow-400">{totalStars}</p>
            <p className="text-xs text-slate-400">total stars</p>
          </div>
          <div>
            <p className="text-xl font-black text-green-400">{activeDaysThisWeek}</p>
            <p className="text-xs text-slate-400">active days</p>
          </div>
        </div>
      )}

      {/* Per-kid cards */}
      {kids.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-4xl mb-3">⚽</p>
          <p className="font-semibold">No players yet.</p>
          <Link href="/onboarding" className="text-green-600 font-bold text-sm mt-1 inline-block">
            Add your first player →
          </Link>
        </div>
      ) : (
        kids.map((kid) => <KidSummaryCard key={kid.id} kid={kid} />)
      )}

      {/* Add player link */}
      {kids.length > 0 && (
        <Link
          href="/onboarding"
          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border-2 border-dashed border-gray-200 text-sm font-semibold text-gray-500 hover:border-green-400 hover:text-green-600 transition-colors"
        >
          + Add Another Player
        </Link>
      )}
    </div>
  )
}
