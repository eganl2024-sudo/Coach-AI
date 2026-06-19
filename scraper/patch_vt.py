"""
patch_vt.py — fixes Virginia Tech name typo in programs.csv,
removes bad-parse VT coach rows, and adds real VT coaches
(scraped from hokiesports.com/sports/mens-soccer/roster).
"""
import csv, os, re

COACHES_PATH  = os.path.join(os.path.dirname(__file__), 'output', 'coaches_enriched.csv')
PROGRAMS_PATH = os.path.join(os.path.dirname(__file__), 'output', 'programs.csv')

FIELDNAMES_COACHES  = ['school_name','first_name','last_name','title','email','phone',
                        'position_focus','twitter_handle','source']
FIELDNAMES_PROGRAMS = ['school_name','conference','region','state','division','program_url','ncaa_id']

OLD_NAME = 'Virginia Polytechnic Instituteand State University'
NEW_NAME = 'Virginia Polytechnic Institute and State University'

# Bad VT coach rows to remove (last_name is a dead giveaway)
BAD_LAST_NAMES = {'coach', 'coaching', 'head', 'support'}

# Real VT coaches
VT_COACHES = [
    {'first_name': 'Mike',    'last_name': 'Brizendine', 'title': 'Head Coach',      'email': 'vtmsoccer@vt.edu', 'phone': ''},
    {'first_name': 'Patrick', 'last_name': 'McSorley',   'title': 'Assistant Coach', 'email': 'vtmsoccer@vt.edu', 'phone': ''},
    {'first_name': 'Jeff',    'last_name': 'Kinney',     'title': 'Assistant Coach', 'email': 'jeffkin@vt.edu',   'phone': '231-7143'},
    {'first_name': 'Kyle',    'last_name': 'Renfro',     'title': 'Assistant Coach', 'email': 'vtmsoccer@vt.edu', 'phone': ''},
]

# ── Fix programs.csv ──────────────────────────────────────────────────────────
with open(PROGRAMS_PATH, newline='', encoding='utf-8') as f:
    programs = list(csv.DictReader(f))

for p in programs:
    if p['school_name'] == OLD_NAME:
        p['school_name'] = NEW_NAME
        p['program_url'] = 'https://hokiesports.com/sports/mens-soccer/roster'
        print(f"Fixed programs.csv: '{OLD_NAME}' -> '{NEW_NAME}'")

with open(PROGRAMS_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES_PROGRAMS, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(programs)

# ── Fix coaches_enriched.csv ──────────────────────────────────────────────────
with open(COACHES_PATH, newline='', encoding='utf-8') as f:
    coaches = list(csv.DictReader(f))

clean = []
removed = 0
for r in coaches:
    # Fix name typo on any existing VT rows (shouldn't be any good ones, but just in case)
    if r['school_name'] == OLD_NAME:
        r['school_name'] = NEW_NAME
    # Remove bad-parse VT rows
    if r['school_name'] == NEW_NAME and r['last_name'].lower() in BAD_LAST_NAMES:
        print(f"  Removing bad row: {r['first_name']} {r['last_name']}")
        removed += 1
        continue
    clean.append(r)

# Add real VT coaches (dedup by name)
existing_keys = {(r['school_name'].lower(), r['first_name'].lower(), r['last_name'].lower()) for r in clean}
added = 0
for c in VT_COACHES:
    key = (NEW_NAME.lower(), c['first_name'].lower(), c['last_name'].lower())
    if key in existing_keys:
        continue
    clean.append({
        'school_name':    NEW_NAME,
        'first_name':     c['first_name'],
        'last_name':      c['last_name'],
        'title':          c['title'],
        'email':          c['email'],
        'phone':          c['phone'],
        'position_focus': '',
        'twitter_handle': '',
        'source':         'manual',
    })
    added += 1

clean.sort(key=lambda r: (r['school_name'], 0 if r['title'] == 'Head Coach' else 1, r['last_name']))

with open(COACHES_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES_COACHES, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(clean)

print(f"Removed {removed} bad VT rows, added {added} real VT coaches. Total: {len(clean)}")
