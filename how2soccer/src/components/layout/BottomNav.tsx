'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Layers, User } from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/skills', label: 'Skills', icon: Layers },
  { href: '/profile', label: 'Profile', icon: User },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t-2 border-gray-100 pb-safe">
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto px-4">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/home' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-colors',
                active ? 'text-green-600' : 'text-gray-400 hover:text-gray-600',
              )}
            >
              <Icon size={22} strokeWidth={active ? 2.5 : 2} />
              <span className={cn('text-xs font-semibold', active ? 'text-green-600' : 'text-gray-400')}>
                {label}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
