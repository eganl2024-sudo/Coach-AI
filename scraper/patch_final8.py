"""
patch_final8.py — fixes the 8 schools with missing emails / bad head coach names.
Removes stale/bad rows then upserts correct data.
"""
import csv, os

COACHES_PATH = os.path.join(os.path.dirname(__file__), 'output', 'coaches_enriched.csv')
FIELDNAMES   = ['school_name','first_name','last_name','title','email','phone',
                'position_focus','twitter_handle','source']

# Rows to remove by (school_name, first_name, last_name) — bad parses or replaced coaches
REMOVE = {
    ('Clemson University',             'Head',  'Coach'),
    ('Long Island University',         'To',    'Be Announced'),
    ('Pennsylvania State University',  'Dow',   'View'),
    ('San Jose State University',      'Head',  'Coach'),
    ('Seattle University',             'Head',  'Coach'),
}

# Coaches to add (skipped if already present by same key)
ADD = [
    # Clemson
    {'school_name': 'Clemson University', 'first_name': 'Mike',  'last_name': 'Noonan', 'title': 'Head Coach',      'email': 'msoccer@clemson.edu', 'phone': ''},
    {'school_name': 'Clemson University', 'first_name': 'Phil',  'last_name': 'Jones',  'title': 'Assistant Coach', 'email': 'msoccer@clemson.edu', 'phone': ''},

    # Penn State (replace "Dow View" with real names)
    {'school_name': 'Pennsylvania State University', 'first_name': 'Rob',  'last_name': 'Dow',  'title': 'Head Coach',      'email': 'msoc@athletics.psu.edu', 'phone': ''},
    {'school_name': 'Pennsylvania State University', 'first_name': 'Brad', 'last_name': 'Cole', 'title': 'Assistant Coach', 'email': 'msoc@athletics.psu.edu', 'phone': ''},

    # San Jose State
    {'school_name': 'San Jose State University', 'first_name': 'Simon',  'last_name': 'Tobin',    'title': 'Head Coach',      'email': 'simon.tobin@sjsu.edu',      'phone': '924-1261'},
    {'school_name': 'San Jose State University', 'first_name': 'Jesus',  'last_name': 'Sanchez',  'title': 'Assistant Coach', 'email': 'jesus.a.sanchez@sjsu.edu',  'phone': '924-1301'},
    {'school_name': 'San Jose State University', 'first_name': 'Jota',   'last_name': 'Yamaguchi','title': 'Assistant Coach', 'email': 'jota.yamaguchi@sjsu.edu',   'phone': ''},
    {'school_name': 'San Jose State University', 'first_name': 'David',  'last_name': 'Sweeney',  'title': 'Assistant Coach', 'email': 'david.sweeney@sjsu.edu',    'phone': ''},

    # Seattle University — use program email for head coach contact
    {'school_name': 'Seattle University', 'first_name': 'Nate',   'last_name': 'Daligcon', 'title': 'Head Coach',      'email': 'msoccer@seattleu.edu', 'phone': ''},
    {'school_name': 'Seattle University', 'first_name': 'Jason',  'last_name': 'Farrell',  'title': 'Assistant Coach', 'email': 'jfarrell2@seattleu.edu','phone': ''},
    {'school_name': 'Seattle University', 'first_name': 'Brooks', 'last_name': 'Hopp',     'title': 'Assistant Coach', 'email': 'bhopp@seattleu.edu',   'phone': ''},

    # Virginia
    {'school_name': 'University of Virginia', 'first_name': 'George',   'last_name': 'Gelnovatch', 'title': 'Head Coach',      'email': 'Vrp9as@virginia.edu',  'phone': '434-982-5701'},
    {'school_name': 'University of Virginia', 'first_name': 'Matt',     'last_name': 'Chulis',     'title': 'Assistant Coach', 'email': 'mrc5r@virginia.edu',   'phone': '434-982-5702'},
    {'school_name': 'University of Virginia', 'first_name': 'Jermaine', 'last_name': 'Birriel',    'title': 'Assistant Coach', 'email': 'vrp9as@virginia.edu',  'phone': '434-982-5125'},
    {'school_name': 'University of Virginia', 'first_name': 'Johnny',   'last_name': 'Fenwick',    'title': 'Assistant Coach', 'email': 'jfenwick@virginia.edu','phone': ''},
]

# Email-only updates for rows that already exist with correct names
EMAIL_UPDATES = {
    # (school_name, first_name, last_name): email
    ('University of California, Davis', 'Dwayne', 'Shaffer'):   'ucdavissoccer@ucd.edu',
    ('University of California, Davis', 'Jason',  'Hotaling'):  'jmhotaling@ucdavis.edu',
}
PHONE_UPDATES = {
    ('University of California, Davis', 'Dwayne', 'Shaffer'):  '(530) 752-8892',
    ('University of California, Davis', 'Jason',  'Hotaling'): '(530) 752-8892',
}

# ── Load ──────────────────────────────────────────────────────────────────────
with open(COACHES_PATH, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Loaded {len(rows)} rows")

# ── Remove bad rows ───────────────────────────────────────────────────────────
clean = []
removed = 0
for r in rows:
    key = (r['school_name'], r['first_name'], r['last_name'])
    if key in REMOVE:
        print(f"  Remove: {r['school_name']} — {r['first_name']} {r['last_name']}")
        removed += 1
    else:
        clean.append(r)

# ── Apply email/phone updates ─────────────────────────────────────────────────
updated = 0
for r in clean:
    key = (r['school_name'], r['first_name'], r['last_name'])
    if key in EMAIL_UPDATES:
        r['email'] = EMAIL_UPDATES[key]
        r['phone'] = PHONE_UPDATES.get(key, r.get('phone', ''))
        print(f"  Updated email: {r['first_name']} {r['last_name']} ({r['school_name']})")
        updated += 1

# ── Add new rows ──────────────────────────────────────────────────────────────
existing = {(r['school_name'].lower(), r['first_name'].lower(), r['last_name'].lower()) for r in clean}
added = 0
for entry in ADD:
    key = (entry['school_name'].lower(), entry['first_name'].lower(), entry['last_name'].lower())
    if key in existing:
        print(f"  Skip (exists): {entry['first_name']} {entry['last_name']} ({entry['school_name']})")
        continue
    clean.append({
        'school_name':    entry['school_name'],
        'first_name':     entry['first_name'],
        'last_name':      entry['last_name'],
        'title':          entry['title'],
        'email':          entry.get('email', ''),
        'phone':          entry.get('phone', ''),
        'position_focus': '',
        'twitter_handle': '',
        'source':         'manual',
    })
    existing.add(key)
    added += 1

clean.sort(key=lambda r: (r['school_name'], 0 if r['title'] == 'Head Coach' else 1, r['last_name']))

with open(COACHES_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(clean)

print(f"\nRemoved {removed}, updated {updated}, added {added}. Total: {len(clean)}")
