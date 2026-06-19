import csv

path = r'C:\Users\ljega\Downloads\Coach AI\scraper\output\coaches_enriched.csv'

BAD_KEYS = {
    ('Old Dominion University',  'soccer',    'coaching'),
    ('Old Dominion University',  'sports',    'performance'),
    ('Old Dominion University',  'soccer',    'support'),
    ('Stanford University',      'soccer',    'coaching'),
    ('Stanford University',      'associate', 'head'),
    ('Stanford University',      'the',       'knowles'),
    ('University of Pittsburgh', 'assistant', 'strength'),
}

FIELDNAMES = ['school_name','first_name','last_name','title','email','phone',
              'position_focus','twitter_handle','source']

with open(path, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

clean = []
removed = 0
for r in rows:
    key = (r['school_name'], r['first_name'].lower(), r['last_name'].lower())
    if key in BAD_KEYS:
        print(f"  Removing bad row: {r['school_name']} | {r['first_name']} {r['last_name']}")
        removed += 1
    else:
        clean.append(r)

with open(path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(clean)

print(f"Removed {removed} bad rows. Total: {len(clean)}")
