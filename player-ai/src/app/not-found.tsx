import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center space-y-6">
        {/* Large green 404 */}
        <h1 className="text-8xl font-black text-primary tracking-tighter">
          404
        </h1>

        {/* Soccer ball emoji */}
        <div className="text-4xl select-none" role="img" aria-label="Soccer ball">
          ⚽
        </div>

        {/* Heading & Subtext */}
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-foreground">
            Page not found
          </h2>
          <p className="text-sm text-muted-foreground max-w-xs mx-auto leading-relaxed">
            This page doesn't exist or you don't have access to it.
          </p>
        </div>

        {/* Stacked / Row buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
          <Button asChild className="w-full sm:w-auto font-semibold">
            <Link href="/">
              Go Home
            </Link>
          </Button>
          <Button asChild variant="outline" className="w-full sm:w-auto font-semibold border-border/50 bg-secondary/35">
            <Link href="/drills">
              Drill Library
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
