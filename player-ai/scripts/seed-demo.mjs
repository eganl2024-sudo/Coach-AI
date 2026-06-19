// scripts/seed-demo.mjs
// Run with: node scripts/seed-demo.mjs

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

// Direct parsing of .env.local to avoid PowerShell encoding bugs on Windows
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

if (!supabaseUrl || !supabaseServiceRoleKey) {
  console.error('❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in env or .env.local');
  process.exit(1);
}

const USERNAME = 'demo';
const PASSWORD = 'PlayerAI2026';

function generateSalt() {
  const bytes = crypto.randomBytes(16);
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.slice(i, i + 2), 16);
  }
  return bytes;
}

async function hashPassword(password, salt) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );
  const bits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      hash: 'SHA-256',
      salt: hexToBytes(salt),
      iterations: 100000,
    },
    keyMaterial,
    256
  );
  return Array.from(new Uint8Array(bits))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

async function main() {
  console.log(`Connecting to Supabase at: ${supabaseUrl}`);
  const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

  // Check if demo already exists
  const { data: existing, error: findError } = await supabase
    .from('users')
    .select('username')
    .eq('username', USERNAME)
    .maybeSingle();

  if (findError) {
    console.error('❌ Failed to check for existing demo user:', findError.message);
    process.exit(1);
  }

  const salt = generateSalt();
  const hash = await hashPassword(PASSWORD, salt);

  if (existing) {
    console.log('Demo account already exists — updating password hash...');
    const { error } = await supabase
      .from('users')
      .update({ password_hash: hash, salt })
      .eq('username', USERNAME);
    if (error) {
      console.error('❌ Failed to update demo account:', error.message);
      process.exit(1);
    }
    console.log('✅ Demo account password updated. Login: demo / PlayerAI2026');
    return;
  }

  const { error } = await supabase
    .from('users')
    .insert({
      username: USERNAME,
      password_hash: hash,
      salt,
      created_at: new Date().toISOString(),
    });

  if (error) {
    console.error('❌ Failed to seed demo account:', error.message);
    console.error('Check that the users table has columns: username, password_hash, salt, created_at');
    process.exit(1);
  }

  console.log('✅ Demo account seeded successfully. Login: demo / PlayerAI2026');
}

main();
