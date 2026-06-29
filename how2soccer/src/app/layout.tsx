import type { Metadata, Viewport } from 'next'
import './globals.css'
import { PostHogProvider } from '@/components/PostHogProvider'

export const metadata: Metadata = {
  title: {
    default: 'How 2 Soccer',
    template: '%s | How 2 Soccer',
  },
  description: 'Learn soccer skills step by step — for kids ages 5–12.',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'How 2 Soccer',
  },
  icons: {
    icon: '/icons/icon.svg',
    apple: '/icons/icon.svg',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#22c55e',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  )
}
