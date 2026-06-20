import { timingSafeEqual } from 'crypto';

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.slice(i, i + 2), 16);
  }
  return bytes;
}

export function generateSalt(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

export async function hashPassword(
  password: string,
  salt: string,
  iterations = 600_000,
): Promise<string> {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(password),
    'PBKDF2',
    false,
    ['deriveBits'],
  );
  const bits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      hash: 'SHA-256',
      salt: hexToBytes(salt) as unknown as BufferSource,
      iterations,
    },
    keyMaterial,
    256,
  );
  return Array.from(new Uint8Array(bits))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * Verifies a password in constant time.
 * Returns { valid, needsRehash } — needsRehash is true when the stored hash
 * used the legacy 100K iteration count and should be transparently upgraded.
 */
export async function verifyPassword(
  password: string,
  salt: string,
  storedHash: string,
): Promise<{ valid: boolean; needsRehash: boolean }> {
  const computed600k = await hashPassword(password, salt, 600_000);

  const aBytes = Buffer.from(computed600k, 'hex');
  const bBytes = Buffer.from(storedHash, 'hex');

  // Buffers must be same length for timingSafeEqual
  if (aBytes.length === bBytes.length && timingSafeEqual(aBytes, bBytes)) {
    return { valid: true, needsRehash: false };
  }

  // Fallback: check legacy 100K hash (accounts created before the bump)
  const computed100k = await hashPassword(password, salt, 100_000);
  const aLegacy = Buffer.from(computed100k, 'hex');

  if (aLegacy.length === bBytes.length && timingSafeEqual(aLegacy, bBytes)) {
    return { valid: true, needsRehash: true };
  }

  return { valid: false, needsRehash: false };
}
