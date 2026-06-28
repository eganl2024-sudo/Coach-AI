import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

interface HeaderProps {
  title?: string
  showBack?: boolean
  backHref?: string
}

export function Header({ title, showBack, backHref = '/skills' }: HeaderProps) {
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
          <Link href="/home" className="flex items-center gap-2">
            <span className="text-2xl">⚽</span>
            <span className="text-xl font-black text-green-600 tracking-tight">How 2 Soccer</span>
          </Link>
        )}
      </div>
    </header>
  )
}
