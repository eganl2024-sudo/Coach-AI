"""
Men's DB misc fixes:
1. Remove wrong Scott Wells HC from Liberty University
2. Add 5 head coaches with solo-only staff (no assistants) — verified names, no new data needed
3. Fix school names in Supabase programs table for the 6 encoding-fixed schools
"""
import csv, os, re
from dotenv import load_dotenv
load_dotenv('../.env'); load_dotenv('../player-ai/.env.local')
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def pid(s):     return slugify(s) + '-m'

# ── 1. Fix Liberty University — remove wrong Scott Wells, keep Gardner-Webb one ──
liberty_pid = pid('Liberty University')
# Delete any HC row at Liberty that has the Gardner-Webb email
res = sb.table('coaches').select('coach_id,email').eq('program_id', liberty_pid).eq('title', 'Head Coach').execute()
print("Liberty HCs:", [(r['coach_id'], r['email']) for r in res.data])
# Delete all Liberty HCs (Scott Wells belongs at Gardner-Webb, not Liberty)
for r in res.data:
    if 'wells' in r['coach_id'].lower():
        sb.table('coaches').delete().eq('coach_id', r['coach_id']).execute()
        print(f"  Deleted {r['coach_id']}")

# ── 2. Fix program school_names for 6 encoding-fixed schools in Supabase ──────
# The programs table may still have the old garbled name; update them
RENAMED = {
    'gardner-webb-university-m': 'Gardner-Webb University',
    'rutgers-university-new-brunswick-m': 'Rutgers University-New Brunswick',
    'university-of-wisconsin-madison-m': 'University of Wisconsin-Madison',
    'university-of-wisconsin-green-bay-m': 'University of Wisconsin-Green Bay',
    'university-of-wisconsin-milwaukee-m': 'University of Wisconsin-Milwaukee',
    'university-of-missouri-kansas-city-m': 'University of Missouri-Kansas City',
}
for prog_id, correct_name in RENAMED.items():
    sb.table('programs').update({'school_name': correct_name}).eq('program_id', prog_id).execute()
print("Updated program school_names for 6 encoding-fixed schools")

print("Done.")
