import { createClient } from '@supabase/supabase-js';

export async function createServerClient() {
  // Use transaction pooler URL in production to avoid exhausting direct connections
  // Set SUPABASE_POOLER_URL to your project's pooler URL (port 6543) in Vercel env vars
  const supabaseUrl = process.env.SUPABASE_POOLER_URL || process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY
    || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

  return createClient(supabaseUrl, supabaseKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
    db: {
      schema: 'public',
    },
  });
}
