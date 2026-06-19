"""Remove all coach rows for schools with fully bad-parse data."""
import csv, os

COACHES_PATH = os.path.join(os.path.dirname(__file__), 'output', 'coaches_enriched.csv')
FIELDNAMES   = ['school_name','first_name','last_name','title','email','phone',
                'position_focus','twitter_handle','source']

# Remove ALL rows for these schools — data is garbage, will be re-added manually
WIPE_SCHOOLS = {
    'San Diego State University',
    'University of Central Florida',
}

with open(COACHES_PATH, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

clean = [r for r in rows if r['school_name'] not in WIPE_SCHOOLS]
removed = len(rows) - len(clean)

with open(COACHES_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(clean)

print(f"Removed {removed} bad rows. Total: {len(clean)}")
