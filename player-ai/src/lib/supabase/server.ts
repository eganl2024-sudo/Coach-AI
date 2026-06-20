import { createClient } from '@supabase/supabase-js';

export async function createServerClient() {
  const supabaseUrl = process.env.SUPABASE_POOLER_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl) {
    throw new Error('NEXT_PUBLIC_SUPABASE_URL is not set. Configure it in .env.local.');
  }
  if (!supabaseKey) {
    // Never fall back to the public anon key for server-side operations —
    // that key is exposed in the client bundle and would bypass RLS.
    throw new Error(
      'SUPABASE_SERVICE_ROLE_KEY is not set. Server-side DB operations require the service role key. ' +
      'Configure it in .env.local (never prefix it with NEXT_PUBLIC_).',
    );
  }

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
