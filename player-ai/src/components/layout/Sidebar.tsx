'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Home, ClipboardList, Zap, User, Rss, Menu, X, TrendingUp, Video, Target } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { logoutAction } from '@/lib/actions/auth';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/',            label: 'Home',            icon: Home },
  { href: '/progress',    label: 'Progress',        icon: TrendingUp },
  { href: '/training',    label: 'Training Plan',   icon: ClipboardList },
  { href: '/feed',        label: 'Mentor Feed',     icon: Rss },
  { href: '/reel',        label: 'Highlight Reel',  icon: Video },
  { href: '/drills',      label: 'Drill Library',   icon: Zap },
  { href: '/recruiting',  label: 'Recruiting',      icon: Target },
  { href: '/profile',     label: 'Profile',         icon: User },
];

interface SidebarProps {
  username: string;
  displayName?: string;
}

export function Sidebar({ username, displayName }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  async function handleLogout() {
    await logoutAction();
    router.push('/login');
    router.refresh();
  }

  const initials = username.slice(0, 2).toUpperCase();

  const handleLinkClick = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* PART A: Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-60 border-r border-border/50 bg-card/50 backdrop-blur-sm shrink-0 h-screen">
        {/* Brand */}
        <div className="px-5 py-6">
          <span className="text-lg font-black tracking-tight text-white font-display">Player AI</span>
        </div>

        <Separator className="opacity-30" />

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-colors',
                  active
                    ? 'bg-primary/15 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                )}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>

        <Separator className="opacity-30" />

        {/* User + Logout */}
        <div className="px-3 py-4 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-primary/20 text-primary text-xs font-bold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium text-foreground truncate">{displayName ?? username}</span>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-muted-foreground hover:text-foreground h-11 px-3 text-sm"
            onClick={handleLogout}
          >
            Sign Out
          </Button>
        </div>
      </aside>

      {/* PART B: Mobile Header Bar */}
      <header className="flex md:hidden items-center justify-between px-4 fixed top-0 left-0 w-full h-14 bg-card/95 backdrop-blur-sm border-b border-border/50 z-40">
        <span className="text-lg font-black tracking-tight text-white font-display">Player AI</span>
        <Button
          onClick={() => setIsOpen(true)}
          variant="ghost"
          size="icon"
          className="w-11 h-11 rounded-md bg-secondary/50 text-foreground hover:bg-secondary"
        >
          <Menu className="w-5 h-5" />
        </Button>
      </header>

      {/* Mobile Drawer Panel */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Slide-in panel */}
          <aside className="relative flex flex-col w-64 bg-card/95 backdrop-blur-sm h-full border-r border-border/50 shadow-2xl">
            {/* Header / Brand & Close */}
            <div className="flex items-center justify-between px-5 py-4">
              <span className="text-lg font-black tracking-tight text-white font-display">Player AI</span>
              <Button
                onClick={() => setIsOpen(false)}
                variant="ghost"
                size="icon"
                className="w-11 h-11 rounded-md text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            <Separator className="opacity-30" />

            {/* Nav */}
            <nav className="flex-1 px-3 py-4 space-y-1">
              {navItems.map(({ href, label, icon: Icon }) => {
                const active = pathname === href;
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={handleLinkClick}
                    className={cn(
                      'flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-colors',
                      active
                        ? 'bg-primary/15 text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                    )}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {label}
                  </Link>
                );
              })}
            </nav>

            <Separator className="opacity-30" />

            {/* User + Logout */}
            <div className="px-3 py-4 space-y-3">
              <div className="flex items-center gap-3 px-2">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-primary/20 text-primary text-xs font-bold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium text-foreground truncate">{displayName ?? username}</span>
              </div>
              <Button
                variant="ghost"
                className="w-full justify-start text-muted-foreground hover:text-foreground h-11 px-3 text-sm"
                onClick={() => {
                  handleLogout();
                  setIsOpen(false);
                }}
              >
                Sign Out
              </Button>
            </div>
          </aside>

          {/* Semi-transparent Overlay */}
          <div
            onClick={() => setIsOpen(false)}
            className="flex-1 bg-black/50 backdrop-blur-sm cursor-pointer"
          />
        </div>
      )}
    </>
  );
}
