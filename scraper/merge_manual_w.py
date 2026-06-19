import csv, os

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
manual_csv  = os.path.join(SCRIPT_DIR, 'data', 'manual_coaches_w_tier1.csv')
enriched_csv = os.path.join(SCRIPT_DIR, 'output', 'coaches_w_enriched.csv')

existing = set()
rows = []
with open(enriched_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)
        existing.add((r['school_name'].strip().lower(), r['first_name'].strip().lower(), r['last_name'].strip().lower()))

added = 0
with open(manual_csv, newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        key = (r['school_name'].strip().lower(), r['first_name'].strip().lower(), r['last_name'].strip().lower())
        if key in existing:
            print(f"  SKIP (exists): {r['school_name']} {r['first_name']} {r['last_name']}")
            continue
        rows.append({
            'school_name':    r['school_name'],
            'first_name':     r['first_name'],
            'last_name':      r['last_name'],
            'title':          r['title'],
            'email':          r.get('email', ''),
            'phone':          r.get('phone', ''),
            'position_focus': '',
            'twitter_handle': '',
            'source':         'manual',
        })
        added += 1

with open(enriched_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {added} coaches. Total now: {len(rows)}")
