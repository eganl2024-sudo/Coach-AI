import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import type { AthleteProfile } from '@/lib/types/player';
import { OnboardingForm } from '@/components/onboarding/OnboardingForm';

export default async function OnboardingPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  // Prevent re-onboarding if profile already exists
  const existingProfile = await getUserData<AthleteProfile>(username, 'athlete_profile');
  if (existingProfile) {
    redirect('/');
  }

  return (
    <div className="min-h-screen w-full bg-background flex flex-col items-center justify-center p-4 md:p-8 relative">
      {/* Dynamic background decor */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background pointer-events-none" />
      
      <div className="w-full max-w-lg text-center mb-6 relative z-10">
        <h1 className="text-xl font-black text-white tracking-wider mb-2 select-none">
          ⚽ PLAYER AI
        </h1>
        <h2 className="text-2xl font-black tracking-tight text-foreground sm:text-3xl">
          Let's build your development plan
        </h2>
        <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold mt-1">
          This takes about 2 minutes
        </p>
      </div>

      <div className="w-full relative z-10">
        <OnboardingForm />
      </div>
    </div>
  );
}
