"""
import_to_supabase.py — imports programs.csv + coaches_enriched.csv into Supabase.

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment or .env.local.
Uses service role key so it can bypass RLS.

Usage:
  python import_to_supabase.py           # dry run — prints what would be upserted
  python import_to_supabase.py --write   # upsert into Supabase
"""

import argparse
import csv
import os
import re
import sys

# ---------------------------------------------------------------------------
# Load env from player-ai/.env.local if not already set
# ---------------------------------------------------------------------------
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', 'player-ai', '.env.local')
    env_path = os.path.normpath(env_path)
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip()
            val = val.split('#')[0].strip()  # strip inline comments
            if key and val and key not in os.environ:
                os.environ[key] = val

load_env()

try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

PROGRAMS_CSV = os.path.join(os.path.dirname(__file__), 'output', 'programs.csv')
COACHES_CSV  = os.path.join(os.path.dirname(__file__), 'output', 'coaches_enriched.csv')

BATCH_SIZE = 100  # Supabase upsert batch size


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def make_program_id(school_name: str) -> str:
    return slugify(school_name)


def make_coach_id(school_name: str, first: str, last: str) -> str:
    return slugify(f"{school_name}-{first}-{last}")


def load_programs() -> list[dict]:
    rows = []
    with open(PROGRAMS_CSV, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append({
                'program_id':  make_program_id(r['school_name']),
                'school_name': r['school_name'].strip(),
                'conference':  r.get('conference', '').strip(),
                'region':      r.get('region', '').strip(),
                'state':       r.get('state', '').strip(),
                'division':    r.get('division', 'D1').strip() or 'D1',
                'program_url': r.get('program_url', '').strip() or None,
                'ncaa_id':     r.get('ncaa_id', '').strip() or None,
            })
    return rows


def load_coaches(program_ids: set[str]) -> list[dict]:
    VALID_TITLES = {'Head Coach', 'Assistant Coach', 'Director of Operations'}
    rows = []
    skipped = 0
    with open(COACHES_CSV, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            school = r['school_name'].strip()
            pid = make_program_id(school)
            if pid not in program_ids:
                print(f"  WARN: No program found for '{school}' — skipping coach {r['first_name']} {r['last_name']}")
                skipped += 1
                continue
            title = r.get('title', '').strip()
            if title not in VALID_TITLES:
                skipped += 1
                continue
            rows.append({
                'coach_id':       make_coach_id(school, r['first_name'], r['last_name']),
                'program_id':     pid,
                'school_name':    school,
                'first_name':     r.get('first_name', '').strip(),
                'last_name':      r.get('last_name', '').strip(),
                'title':          title,
                'email':          r.get('email', '').strip() or None,
                'phone':          r.get('phone', '').strip() or None,
                'position_focus': r.get('position_focus', '').strip() or None,
                'twitter_handle': r.get('twitter_handle', '').strip() or None,
                'source':         r.get('source', 'scrape').strip() or 'scrape',
            })
    if skipped:
        print(f"  Skipped {skipped} coach rows (no matching program or invalid title)")
    return rows


def upsert_batched(supabase, table: str, rows: list[dict], id_col: str):
    total = len(rows)
    inserted = 0
    for i in range(0, total, BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        res = supabase.table(table).upsert(batch, on_conflict=id_col).execute()
        inserted += len(batch)
        print(f"  {table}: {inserted}/{total} upserted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Actually upsert into Supabase')
    args = parser.parse_args()

    programs = load_programs()
    program_ids = {p['program_id'] for p in programs}
    coaches = load_coaches(program_ids)

    print(f"\nReady to import:")
    print(f"  {len(programs)} programs")
    print(f"  {len(coaches)} coaches")
    print(f"  Head coaches: {sum(1 for c in coaches if c['title'] == 'Head Coach')}")
    print(f"  With email:   {sum(1 for c in coaches if c['email'])}")

    if not args.write:
        print("\nDry run — pass --write to import into Supabase")
        print("\nSample programs:")
        for p in programs[:3]:
            print(f"  {p['program_id']} | {p['school_name']} | {p['conference']} | {p['state']}")
        print("\nSample coaches:")
        for c in coaches[:5]:
            print(f"  {c['coach_id']} | {c['title']} | {c['email'] or '(no email)'}")
        return

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nERROR: NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)

    print(f"\nConnecting to {SUPABASE_URL} ...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\nUpserting programs ...")
    upsert_batched(supabase, 'programs', programs, 'program_id')

    print("\nUpserting coaches ...")
    upsert_batched(supabase, 'coaches', coaches, 'coach_id')

    print(f"\nDone. {len(programs)} programs, {len(coaches)} coaches imported.")


if __name__ == '__main__':
    main()
