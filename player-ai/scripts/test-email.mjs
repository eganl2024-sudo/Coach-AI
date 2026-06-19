// scripts/test-email.mjs
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';

// Direct parsing of .env.local
let supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
let supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

try {
  const envPath = path.resolve(process.cwd(), '.env.local');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    envContent.split(/\r?\n/).forEach(line => {
      const parts = line.split('=');
      if (parts.length >= 2) {
        const key = parts[0].trim();
        const value = parts.slice(1).join('=').trim();
        if (key === 'NEXT_PUBLIC_SUPABASE_URL') {
          supabaseUrl = value;
        }
        if (key === 'SUPABASE_SERVICE_ROLE_KEY') {
          supabaseServiceRoleKey = value;
        }
      }
    });
  }
} catch (err) {
  console.error('⚠️ Failed to load env from .env.local:', err.message);
}

const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

// We need to import calculateRRS and sendWeeklySummaryEmail from our app
// Let's import the sendWeeklySummaryEmail by copying or running a script that runs it
// Since ES Modules imports relative to src are supported, let's import it directly!
// But wait, the file has paths relative to @/lib/...
// Let's resolve the path using node or simply run a test in the context of our app by writing a simple script that mocks the action!
// Wait, can we mock imports or just write a small Node test?
// Since next-env and path aliases are configured, running a script with node might not resolve @/lib.
// However, we can write the test using standard relative paths!
// Let's read sendWeeklySummaryEmail from src/lib/email/resend.ts.
// In resend.ts:
// import { calculateRRS } from '@/lib/utils/calculateRRS';
// Node won't resolve `@/lib/` out of the box.
// But we can resolve it using a small tool, or we can just run a ts-node / next context or simply construct a small script!
// Let's see: can we write a node script that registers path aliases, or simply runs in a way that resolves them?
// Actually, we can use the `module-alias` package, or we can run next in dev mode and request a test endpoint!
// Yes!!! A test API endpoint like `/api/debug/email` is 100% standard in Next.js, executes in the FULL Next.js context (meaning all path aliases are resolved correctly), and can be hit using fetch!
// This is incredibly elegant and avoids any module resolution hacking!
