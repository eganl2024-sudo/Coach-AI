"""
Upserts only the corrected/patched schools to Supabase, rather than
reimporting the entire women's dataset.
"""
import csv, os, re, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'player-ai', '.env.local'))
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb = create_client(url, key)

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
ENRICHED    = os.path.join(SCRIPT_DIR, 'output', 'coaches_w_enriched.csv')
PROGRAMS_W  = os.path.join(SCRIPT_DIR, 'output', 'programs_w.csv')

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def make_program_id(school):
    return slugify(school) + '-w'

def make_coach_id(school, first, last):
    return slugify(f"{school}-w-{first}-{last}")

# Targeted schools — those we just corrected
CORRECTED_SCHOOLS = {
    # Full replacements
    'Alabama','Georgia','Texas','Texas A&M','Texas Tech','North Carolina',
    'Michigan','Michigan State','Purdue','Nebraska','Ohio','Oregon','Washington State',
    # Auto-removed HC only (these just need the wrong HC deleted, assistants may be fine)
    'Alabama A&M','Alabama State','Arkansas','Arkansas State','Charleston Southern',
    'Delaware State','Eastern Kentucky','Eastern Washington','Houston','Loyola Chicago',
    'Missouri','Nevada','Northwestern State','Southeast Missouri State','Southern Illinois',
    'Southern Utah','Tarleton State','Texas State','Utah','Utah State',
    'Wagner','West Georgia','Western Kentucky',
}

# Load program_id map
program_map = {}
for r in csv.DictReader(open(PROGRAMS_W, newline='', encoding='utf-8')):
    program_map[r['school_name']] = make_program_id(r['school_name'])

# Load all coaches for targeted schools
coaches_to_upsert = []
all_coaches = list(csv.DictReader(open(ENRICHED, newline='', encoding='utf-8')))
for r in all_coaches:
    if r['school_name'] not in CORRECTED_SCHOOLS:
        continue
    pid = program_map.get(r['school_name'])
    if not pid:
        continue
    coaches_to_upsert.append({
        'coach_id':       make_coach_id(r['school_name'], r['first_name'], r['last_name']),
        'program_id':     pid,
        'school_name':    r['school_name'].strip(),
        'first_name':     r['first_name'].strip(),
        'last_name':      r['last_name'].strip(),
        'title':          r['title'].strip(),
        'email':          r['email'].strip(),
        'phone':          r['phone'].strip(),
        'position_focus': r.get('position_focus','').strip(),
        'source':         r.get('source','manual').strip(),
    })

# Delete existing coaches for these schools first
pids_to_clear = [program_map[s] for s in CORRECTED_SCHOOLS if s in program_map]
print(f"Clearing coaches for {len(pids_to_clear)} programs...")
for i in range(0, len(pids_to_clear), 20):
    batch = pids_to_clear[i:i+20]
    sb.table('coaches').delete().in_('program_id', batch).execute()

# Upsert corrected coaches
print(f"Upserting {len(coaches_to_upsert)} corrected coaches...")
for i in range(0, len(coaches_to_upsert), 50):
    batch = coaches_to_upsert[i:i+50]
    sb.table('coaches').upsert(batch, on_conflict='coach_id').execute()
    print(f"  {min(i+50, len(coaches_to_upsert))}/{len(coaches_to_upsert)}")

print("Done.")
