import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'How 2 Soccer',
    template: '%s | How 2 Soccer',
  },
  description: 'Learn soccer skills step by step — for kids ages 5–12.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
