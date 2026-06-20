"""
Normalizes em-dash / replacement-char school names in programs.csv and
coaches_enriched.csv (both encodings: U+FFFD and ASCII '?'), then imports
the 6 previously-missing schools into Supabase.
"""
import csv, os, re
from dotenv import load_dotenv
load_dotenv('../.env'); load_dotenv('../player-ai/.env.local')
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

PROGRAMS_M = 'output/programs.csv'
COACHES_M  = 'output/coaches_enriched.csv'

DASH_CHARS = '–—‒�'  # en-dash, em-dash, figure-dash, replacement-char

def normalize_name(name: str) -> str:
    """Replace any dash-like or replacement char (including ASCII '?') with '-'."""
    # First handle Unicode dash variants and replacement char
    for ch in DASH_CHARS:
        name = name.replace(ch, '-')
    # Handle cases where scraper stored '?' instead of a dash (e.g., Gardner?Webb)
    # Only between word characters (not at start/end, not in real question context)
    name = re.sub(r'(?<=[A-Za-z])\?(?=[A-Za-z])', '-', name)
    # Collapse whitespace around hyphens
    name = re.sub(r'\s*-\s*', '-', name)
    return name.strip()

# ── Fix programs.csv ────────────────────────────────────────────────────────
rows = []
with open(PROGRAMS_M, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f); fn = reader.fieldnames
    for r in reader:
        r['school_name'] = normalize_name(r['school_name'])
        rows.append(r)
with open(PROGRAMS_M, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); w.writerows(rows)
print(f"Fixed {PROGRAMS_M}  ({len(rows)} rows)")

# ── Fix coaches_enriched.csv ────────────────────────────────────────────────
rows = []
with open(COACHES_M, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f); fn = reader.fieldnames
    for r in reader:
        r['school_name'] = normalize_name(r['school_name'])
        rows.append(r)
with open(COACHES_M, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); w.writerows(rows)
print(f"Fixed {COACHES_M}  ({len(rows)} rows)")

# Verify fix
problem_schools = ['Gardner-Webb University', 'Rutgers University-New Brunswick',
                   'University of Wisconsin-Madison', 'University of Missouri-Kansas City']
coach_school_names = set(r['school_name'] for r in rows)
for s in problem_schools:
    found = s in coach_school_names
    print(f"  {'OK' if found else 'STILL MISSING'}: {s}")

# ── Reimport the 6 previously-missing schools ───────────────────────────────
def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def pid(s):     return slugify(s)
def cid(s,f,l): return slugify(f'{s}-{f}-{l}')

MISSING = {
    'Gardner-Webb University',
    'Rutgers University-New Brunswick',
    'University of Wisconsin-Madison',
    'University of Wisconsin-Green Bay',
    'University of Wisconsin-Milwaukee',
    'University of Missouri-Kansas City',
}

coaches  = list(csv.DictReader(open(COACHES_M, newline='', encoding='utf-8')))
programs = list(csv.DictReader(open(PROGRAMS_M, newline='', encoding='utf-8')))
program_map = {r['school_name']: pid(r['school_name']) for r in programs}

target_coaches = [c for c in coaches if c['school_name'] in MISSING]
target_pids    = [program_map[s] for s in MISSING if s in program_map]

print(f"\nReimporting {len(MISSING)} schools, {len(target_coaches)} coaches...")

# Programs already exist in Supabase with correct IDs — skip upsert
print("  Programs already exist, skipping upsert")

for p in target_pids:
    sb.table('coaches').delete().eq('program_id', p).execute()

coach_rows = [{'coach_id': cid(r['school_name'], r['first_name'], r['last_name']),
               'program_id': program_map[r['school_name']], 'school_name': r['school_name'],
               'first_name': r['first_name'], 'last_name': r['last_name'],
               'title': r['title'], 'email': r['email'], 'phone': r['phone'],
               'position_focus': r.get('position_focus',''), 'source': r.get('source','scrape')}
              for r in target_coaches]

for i in range(0, len(coach_rows), 50):
    sb.table('coaches').upsert(coach_rows[i:i+50], on_conflict='coach_id').execute()

print(f"  Inserted {len(coach_rows)} coaches")
print("Done.")
