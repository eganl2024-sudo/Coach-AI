"""
apply_corrections_w.py — Two-pass correction of coaches_w_enriched.csv:

Pass 1: Auto-remove duplicate HC entries where the email domain identifies the
        wrong school. Only removes the Head Coach row; leaves other staff.

Pass 2: For schools with provided corrections (manual_corrections_w.csv):
        - Delete ALL existing coach rows for that school
        - Insert the correct rows from the corrections file

Run:    python apply_corrections_w.py [--dry-run]
"""
import argparse
import csv
import os

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
ENRICHED      = os.path.join(SCRIPT_DIR, 'output', 'coaches_w_enriched.csv')
CORRECTIONS   = os.path.join(SCRIPT_DIR, 'data', 'manual_corrections_w.csv')

# ── Pass 1: email-domain resolution ────────────────────────────────────────
# For each duplicate group, which school KEEPS the coach (based on email domain)
# All other schools in the group get their wrong HC row removed.
WRONG_HC_SCHOOLS = {
    # group: (correct school, [wrong schools])
    'Caroline Kelly':    ('Oregon State',      ['Oregon']),
    'Christian Michner': ('Charleston',         ['Charleston Southern']),
    'Derek Burton':      ('SIU Edwardsville',   ['Southern Illinois']),
    'Derek Nichols':     ('Central Arkansas',   ['Arkansas', 'Arkansas State']),
    'Ed Joyce':          ('Georgia State',      ['Georgia', 'West Georgia']),
    'Gary Higgins':      ('NC State',           ['North Carolina']),
    'Jason Burr':        ('Purdue Fort Wayne',  ['Purdue']),
    'Kacey Bingham':     ('UNLV',               ['Nevada']),
    'Kelly Lawrence':    ('Delaware',           ['Delaware State']),
    'Kevin Larry':       ('Chicago State',      ['Loyola Chicago']),
    'Kirk Nelson':       ('Missouri State',     ['Missouri', 'Southeast Missouri State']),
    'Lexi Brown':        ('Utah Tech',          ['Southern Utah', 'Utah', 'Utah State']),
    'Lisa Mann':         ('UAB',                ['Alabama', 'Alabama A&M', 'Alabama State']),
    'Lori Walker-Hock':  ('Ohio State',         ['Ohio']),
    'Michael Moynihan':  ('Northwestern',       ['Northwestern State']),
    'Nataki Stewart':    ('UT Rio Grande Valley',['Texas', 'Texas A&M', 'Texas State', 'Texas Tech']),
    'Nick Whiting':      ('Houston Christian',  ['Houston']),
    'Nicole Van Dyke':   ('Washington',         ['Eastern Washington', 'Washington State']),
    'Pete Cuadrado':     ('Coastal Carolina',   ['Tarleton State']),
    'Phil Casella':      ('American',           ['Wagner']),
    'Tim Walters':       ('Omaha',              ['Nebraska']),
    'Troy Fabiano':      ('Kentucky',           ['Eastern Kentucky', 'Western Kentucky']),
}

# Build the set of (school, coach_name) pairs to auto-remove
auto_remove = set()
for coach_name, (correct, wrong_list) in WRONG_HC_SCHOOLS.items():
    for school in wrong_list:
        auto_remove.add((school, coach_name))

# Schools getting full replacement from corrections file
corrections_rows = list(csv.DictReader(open(CORRECTIONS, newline='', encoding='utf-8')))
replace_schools  = set(r['school_name'] for r in corrections_rows)


def main(dry_run=False):
    original = list(csv.DictReader(open(ENRICHED, newline='', encoding='utf-8')))
    fieldnames = list(original[0].keys())

    kept, auto_removed, replaced = [], [], []
    remove_counts = {}

    for row in original:
        school = row['school_name']
        name   = f"{row['first_name']} {row['last_name']}"

        # Pass 2: full replacement schools — drop all existing rows
        if school in replace_schools:
            replaced.append(row)
            continue

        # Pass 1: auto-remove wrong HC rows
        if row['title'] == 'Head Coach' and (school, name) in auto_remove:
            remove_counts[school] = remove_counts.get(school, 0) + 1
            auto_removed.append(row)
            continue

        kept.append(row)

    # Append corrections
    new_rows = []
    for r in corrections_rows:
        new_rows.append({
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

    final = kept + new_rows

    print(f"Original rows:        {len(original)}")
    print(f"Auto-removed HC rows: {len(auto_removed)}")
    print(f"Full-replace removed: {len(replaced)}")
    print(f"Corrections added:    {len(new_rows)}")
    print(f"Final rows:           {len(final)}")
    print()
    print("Auto-removed HC (wrong school):")
    for row in auto_removed:
        print(f"  {row['school_name']}: {row['first_name']} {row['last_name']}")
    print()
    print("Full-replaced schools (all staff reloaded):")
    for s in sorted(replace_schools):
        old = sum(1 for r in replaced if r['school_name'] == s)
        new = sum(1 for r in new_rows if r['school_name'] == s)
        print(f"  {s}: removed {old}, added {new}")

    if dry_run:
        print("\n[dry-run] No changes written.")
        return

    with open(ENRICHED, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final)
    print("\nWrote corrected data to", ENRICHED)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    main(dry_run=args.dry_run)
