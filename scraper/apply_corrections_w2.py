"""
apply_corrections_w2.py — Second corrections pass.

Full-replaces all schools in manual_corrections_w2.csv, then re-imports
Tarleton State and Wagner which were incorrectly auto-removed in pass 1.
"""
import argparse, csv, os

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ENRICHED     = os.path.join(SCRIPT_DIR, 'output', 'coaches_w_enriched.csv')
CORRECTIONS  = os.path.join(SCRIPT_DIR, 'data', 'manual_corrections_w2.csv')

corrections_rows = list(csv.DictReader(open(CORRECTIONS, newline='', encoding='utf-8')))
replace_schools  = set(r['school_name'] for r in corrections_rows)

def main(dry_run=False):
    original = list(csv.DictReader(open(ENRICHED, newline='', encoding='utf-8')))
    fieldnames = list(original[0].keys())

    kept, replaced = [], []
    for row in original:
        if row['school_name'] in replace_schools:
            replaced.append(row)
        else:
            kept.append(row)

    new_rows = [{
        'school_name':    r['school_name'],
        'first_name':     r['first_name'],
        'last_name':      r['last_name'],
        'title':          r['title'],
        'email':          r.get('email', ''),
        'phone':          r.get('phone', ''),
        'position_focus': '',
        'twitter_handle': '',
        'source':         'manual',
    } for r in corrections_rows]

    final = kept + new_rows

    print(f"Original:  {len(original)}")
    print(f"Removed:   {len(replaced)}  (from {len(replace_schools)} schools)")
    print(f"Added:     {len(new_rows)}")
    print(f"Final:     {len(final)}")
    print()
    for s in sorted(replace_schools):
        old = sum(1 for r in replaced if r['school_name'] == s)
        new = sum(1 for r in new_rows if r['school_name'] == s)
        print(f"  {s}: -{old} +{new}")

    if dry_run:
        print("\n[dry-run] No changes written.")
        return

    with open(ENRICHED, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final)
    print(f"\nWrote {len(final)} rows to {ENRICHED}")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    main(dry_run=p.parse_args().dry_run)
