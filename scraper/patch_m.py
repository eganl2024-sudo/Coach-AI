import csv, os, re
from dotenv import load_dotenv
load_dotenv('../.env'); load_dotenv('../player-ai/.env.local')
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def pid(s):     return slugify(s)          # men's programs have no gender suffix
def cid(s,f,l): return slugify(f'{s}-{f}-{l}')

programs = list(csv.DictReader(open('output/programs.csv', encoding='utf-8')))
program_map = {r['school_name']: pid(r['school_name']) for r in programs}

patch = list(csv.DictReader(open('data/manual_patch_m.csv', encoding='utf-8')))
schools = set(r['school_name'] for r in patch)

# Verify all names match
unmatched = [s for s in schools if s not in program_map]
if unmatched:
    print("WARNING no program_id:", unmatched)
    exit(1)

pids = [program_map[s] for s in schools]
print(f"Clearing {len(pids)} programs...")
for i in range(0, len(pids), 20):
    sb.table('coaches').delete().in_('program_id', pids[i:i+20]).execute()

rows = [{'coach_id': cid(r['school_name'], r['first_name'], r['last_name']),
         'program_id': program_map[r['school_name']], 'school_name': r['school_name'],
         'first_name': r['first_name'], 'last_name': r['last_name'],
         'title': r['title'], 'email': r['email'], 'phone': r['phone'],
         'position_focus': '', 'source': 'manual'}
        for r in patch]

print(f"Inserting {len(rows)} coaches...")
for i in range(0, len(rows), 50):
    sb.table('coaches').upsert(rows[i:i+50], on_conflict='coach_id').execute()

# Merge into CSV
ENRICHED = 'output/coaches_enriched.csv'
existing = []
fn = None
with open(ENRICHED, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f); fn = reader.fieldnames
    for row in reader:
        if row['school_name'] not in schools:
            existing.append(row)
for r in patch:
    existing.append({'school_name':r['school_name'],'first_name':r['first_name'],
                     'last_name':r['last_name'],'title':r['title'],'email':r['email'],
                     'phone':r['phone'],'position_focus':'','twitter_handle':'','source':'manual'})
with open(ENRICHED, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); w.writerows(existing)

print(f"Done. Total men's coaches: {len(existing)}")
