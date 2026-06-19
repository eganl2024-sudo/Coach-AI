// scripts/patch-demo-email.mjs
// Run with: node scripts/patch-demo-email.mjs
// Edit DEMO_EMAIL below to your real email address before running

import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';

// Read .env.local manually
const envContent = readFileSync('.env.local', 'utf8');
const envVars = {};
for (const line of envContent.split('\n')) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) continue;
  const idx = trimmed.indexOf('=');
  if (idx === -1) continue;
  envVars[trimmed.slice(0, idx).trim()] = trimmed.slice(idx + 1).trim();
}

const SUPABASE_URL = envVars['NEXT_PUBLIC_SUPABASE_URL'];
const SUPABASE_KEY = envVars['SUPABASE_SERVICE_ROLE_KEY'];

// ← CHANGE THIS to your real email before running
const DEMO_EMAIL = 'your-real-email@example.com';
const USERNAME = 'demo';

async function main() {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.error('Missing Supabase credentials in .env.local');
    process.exit(1);
  }

  if (DEMO_EMAIL === 'your-real-email@example.com') {
    console.error('❌ Edit DEMO_EMAIL in this script to your real email address first!');
    process.exit(1);
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  // Fetch current athlete_profile
  const { data, error } = await supabase
    .from('user_data')
    .select('data_value')
    .eq('username', USERNAME)
    .eq('data_key', 'athlete_profile')
    .single();

  if (error || !data) {
    console.error('Failed to fetch demo athlete_profile:', error?.message);
    process.exit(1);
  }

  // Parse, add email, re-save
  const profile = JSON.parse(data.data_value);
  const previousEmail = profile.email ?? '(none)';
  profile.email = DEMO_EMAIL;

  const { error: updateError } = await supabase
    .from('user_data')
    .update({
      data_value: JSON.stringify(profile),
      updated_at: new Date().toISOString(),
    })
    .eq('username', USERNAME)
    .eq('data_key', 'athlete_profile');

  if (updateError) {
    console.error('Failed to update demo profile:', updateError.message);
    process.exit(1);
  }

  console.log(`✅ Demo account email updated.`);
  console.log(`   Previous email : ${previousEmail}`);
  console.log(`   New email      : ${DEMO_EMAIL}`);
  console.log('');
  console.log('You can now test the weekly email by completing a week and clicking Generate Next Week.');
}

main();
