import Link from 'next/link'
import { ArrowLeft, Settings } from 'lucide-react'
import { getSession } from '@/lib/session'

interface HeaderProps {
  title?: string
  showBack?: boolean
  backHref?: string
}

export async function Header({ title, showBack, backHref = '/skills' }: HeaderProps) {
  const session = await getSession()
  const showSettings = !!session.parentId

  return (
    <header className="sticky top-0 z-40 bg-white border-b-2 border-gray-100 flex justify-center">
      <div className="flex items-center h-14 px-4 max-w-lg w-full gap-3">
        {showBack && (
          <Link
            href={backHref}
            className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft size={20} />
          </Link>
        )}

        {title ? (
          <h1 className="text-lg font-bold text-gray-900 flex-1">{title}</h1>
        ) : (
          <Link href="/home" className="flex items-center gap-2 flex-1">
            <span className="text-2xl">⚽</span>
            <span className="text-xl font-black text-green-600 tracking-tight">How 2 Soccer</span>
          </Link>
        )}

        {showSettings && (
          <Link
            href="/settings"
            className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            aria-label="Settings"
          >
            <Settings size={20} />
          </Link>
        )}
      </div>
    </header>
  )
}
