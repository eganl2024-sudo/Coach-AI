import type { Metadata, Viewport } from 'next'
import { Nunito } from 'next/font/google'
import './globals.css'
import { PostHogProvider } from '@/components/PostHogProvider'

const nunito = Nunito({
  subsets: ['latin'],
  variable: '--font-nunito',
  display: 'swap',
  weight: ['400', '600', '700', '800', '900'],
})

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
      <body className={nunito.variable}>
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  )
}
