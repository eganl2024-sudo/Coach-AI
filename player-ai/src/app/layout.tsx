import type { Metadata } from 'next';
import { Inter, Barlow_Condensed } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });
const barlowCondensed = Barlow_Condensed({
  subsets: ['latin'],
  weight: ['600', '700', '800'],
  variable: '--font-barlow',
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'https://playerai.app'),
  title: {
    default: 'Player AI',
    template: '%s | Player AI',
  },
  description: 'The personal soccer development platform for serious youth athletes. Track your training, unlock your Recruit Readiness Score, and get discovered.',
  openGraph: {
    type: 'website',
    siteName: 'Player AI',
    title: 'Player AI — Soccer Development for Serious Athletes',
    description: 'Track your training, unlock your RRS score, and build the highlight reel that gets you recruited.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Player AI — Soccer Development Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Player AI — Soccer Development for Serious Athletes',
    description: 'Track your training, unlock your RRS score, and build the highlight reel that gets you recruited.',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} ${barlowCondensed.variable}`}>{children}</body>
    </html>
  );
}
