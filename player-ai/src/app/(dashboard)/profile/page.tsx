import { redirect } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import ProfileEditForm from '@/components/profile/ProfileEditForm';
import ChangePasswordForm from '@/components/profile/ChangePasswordForm';
import DangerZone from '@/components/profile/DangerZone';
import type { AthleteProfile } from '@/lib/types/player';

export const metadata = {
  title: 'My Profile',
};

export default async function ProfilePage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');

  if (!profile) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <h2 className="text-xl font-bold text-white">Profile not found</h2>
        <p className="text-muted-foreground text-sm">
          Please contact support to initialize your player profile.
        </p>
        <Link
          href="/"
          className="inline-block text-primary hover:underline text-sm font-semibold"
        >
          ← Back to Home
        </Link>
      </div>
    );
  }

  const formatMemberSince = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    } catch {
      return 'May 2026';
    }
  };

  const hasSecondaryPosition = profile.secondary_position && profile.secondary_position.toLowerCase() !== 'none';

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 1. Page Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight">My Profile</h1>
          <p className="text-muted-foreground text-xs mt-1">
            Your player identity and development goals.
          </p>
        </div>
        <a
          href="#edit-profile"
          className="shrink-0 inline-flex items-center gap-1.5 text-sm font-semibold text-primary border border-primary/30 bg-primary/10 hover:bg-primary/20 transition-colors px-4 min-h-[44px] rounded-lg mt-1"
        >
          Edit Profile ↓
        </a>
      </div>

      {/* 2. Player Identity Card */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm overflow-hidden">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 divide-y md:divide-y-0 md:divide-x divide-border/50">
            {/* Left Column — Player Info */}
            <div className="space-y-4 pb-6 md:pb-0">
              <div className="space-y-2">
                <h2 className="text-3xl font-black text-white tracking-tight">
                  {profile.name}
                </h2>
                <div className="flex flex-wrap gap-2 items-center">
                  <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 px-3 py-0.5 font-semibold text-xs rounded-md">
                    {profile.position}
                  </Badge>
                  {hasSecondaryPosition && (
                    <Badge variant="secondary" className="text-muted-foreground text-xs px-2.5 py-0.5 rounded-md">
                      {profile.secondary_position}
                    </Badge>
                  )}
                </div>
              </div>

              <div className="space-y-1.5 text-sm text-muted-foreground">
                <p>
                  Age:{' '}
                  <span className="text-foreground font-semibold">
                    {profile.age} years old
                  </span>
                </p>
                <p>
                  Age Group:{' '}
                  <span className="text-foreground font-semibold">
                    {profile.age_group}
                  </span>
                </p>
                <p>
                  Preferred Foot:{' '}
                  <span className="text-foreground font-semibold">
                    {profile.preferred_foot}
                  </span>
                </p>
              </div>
            </div>

            {/* Right Column — Development Goals */}
            <div className="space-y-4 pt-6 md:pt-0 md:pl-8">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground/80">
                Development Goals
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[10px] uppercase font-semibold text-muted-foreground">Current Level</p>
                  <p className="text-sm font-bold text-foreground mt-0.5">{profile.level}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-semibold text-muted-foreground">Target</p>
                  <p className="text-sm font-bold text-primary mt-0.5">{profile.target_level}</p>
                </div>
              </div>

              <div className="space-y-1 text-sm text-muted-foreground">
                <p>
                  Training Commitment:{' '}
                  <span className="text-foreground font-semibold">
                    {profile.sessions_per_week} sessions/week · {profile.session_duration} min each
                  </span>
                </p>
                <p>
                  Member since:{' '}
                  <span className="text-foreground font-semibold">
                    {formatMemberSince(profile.created_date)}
                  </span>
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3. Focus Areas Section */}
      <div className="space-y-3">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Focus Areas</h2>
          <p className="text-xs text-muted-foreground">What you are actively developing this cycle</p>
        </div>
        {profile.focus_areas && profile.focus_areas.length > 0 ? (
          <div className="flex flex-wrap gap-2.5">
            {profile.focus_areas.map((area) => (
              <Badge
                key={area}
                className="bg-primary/10 text-primary border border-primary/20 text-sm font-semibold px-4 py-2 rounded-full"
              >
                {area}
              </Badge>
            ))}
          </div>
        ) : (
          <p className="text-xs text-muted-foreground italic">No focus areas specified.</p>
        )}
      </div>

      {/* 4. Equipment Section */}
      <div className="space-y-3">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Available Equipment</h2>
          <p className="text-xs text-muted-foreground">Drills are matched to what you have</p>
        </div>
        {profile.equipment_available && profile.equipment_available.length > 0 ? (
          <div className="flex flex-wrap gap-2.5">
            {profile.equipment_available.map((item) => (
              <Badge
                key={item}
                className="bg-secondary text-muted-foreground border border-border/50 text-sm font-semibold px-4 py-2 rounded-full"
              >
                {item}
              </Badge>
            ))}
          </div>
        ) : (
          <p className="text-xs text-muted-foreground italic">No equipment specified.</p>
        )}
      </div>

      {/* 5. Academic Profile Section */}
      {(profile.gpa || profile.act_score || profile.sat_score) && (
        <div className="space-y-3">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Academic Profile</h2>
            <p className="text-xs text-muted-foreground">Included in your AI-drafted recruiting emails</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {profile.gpa && (
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/40 border border-border/50">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">GPA</span>
                <span className="text-sm font-black text-white">{profile.gpa}</span>
                {profile.gpa_scale && (
                  <span className="text-[10px] text-muted-foreground">/ {profile.gpa_scale}</span>
                )}
              </div>
            )}
            {profile.act_score && (
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/40 border border-border/50">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">ACT</span>
                <span className="text-sm font-black text-white">{profile.act_score}</span>
              </div>
            )}
            {profile.sat_score && (
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card/40 border border-border/50">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">SAT</span>
                <span className="text-sm font-black text-white">{profile.sat_score}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 6. Profile Edit Form Section */}
      <div id="edit-profile" className="space-y-4 pt-4 border-t border-border/30">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            Edit Profile
          </h2>
          <p className="text-xs text-muted-foreground">
            Update your details — changes to position, focus areas,
            or schedule can regenerate your training plan.
          </p>
        </div>
        <ProfileEditForm profile={profile} username={username} />
      </div>

      {/* 7. Account Security Section */}
      <div className="space-y-4 pt-4 border-t border-border/30">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Account Security</h2>
          <p className="text-xs text-muted-foreground">
            Update your password. Google sign-in accounts cannot set a password.
          </p>
        </div>
        <ChangePasswordForm />
      </div>

      {/* 8. Danger Zone Section */}
      <div className="space-y-4 pt-4 border-t border-destructive/20">
        <div>
          <h2 className="text-lg font-bold text-destructive tracking-tight">Danger Zone</h2>
          <p className="text-xs text-muted-foreground">
            Irreversible account actions.
          </p>
        </div>
        <DangerZone username={username} />
      </div>
    </div>
  );
}
