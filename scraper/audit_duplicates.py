"""
For each duplicate group, use the email domain to identify the correct school.
Print: KEEP (real school), FIX NEEDED (wrong schools to correct).
"""
import csv
from collections import defaultdict

coaches = list(csv.DictReader(open('output/coaches_w_enriched.csv', encoding='utf-8')))

hc_by_school = {}
for c in coaches:
    if c['title'] == 'Head Coach':
        hc_by_school[c['school_name']] = c

hc_names = defaultdict(list)
for school, hc in hc_by_school.items():
    name = f"{hc['first_name']} {hc['last_name']}"
    hc_names[name].append(school)

duplicates = {n: ss for n, ss in hc_names.items() if len(ss) > 1}

# Map known email domains → school hint
DOMAIN_HINTS = {
    'oregonstate.edu': 'Oregon State',
    'cofc.edu': 'Charleston',
    'siue.edu': 'SIU Edwardsville',
    'uca.edu': 'Central Arkansas',
    'gsu.edu': 'Georgia State',
    'ncsu.edu': 'NC State',
    'pfw.edu': 'Purdue Fort Wayne',
    'unlv.edu': 'UNLV',
    'udel.edu': 'Delaware',
    'csu.edu': 'Chicago State',
    'missouristate.edu': 'Missouri State',
    'utahtech.edu': 'Utah Tech',
    'uab.edu': 'UAB',
    'osu.edu': 'Ohio State',
    'northwestern.edu': 'Northwestern',
    'utrgv.edu': 'UT Rio Grande Valley',
    'hc.edu': 'Houston Christian',
    'uw.edu': 'Washington',
    'omavs.com': 'Omaha',
    'uky.edu': 'Kentucky',
    'tarleton.edu': 'Tarleton State',
    'coastal.edu': 'Coastal Carolina',
    'american.edu': 'American',
    'wagner.edu': 'Wagner',
}

needs_manual = []
auto_resolved = []

print("CORRECTIONS NEEDED BY GROUP")
print("=" * 60)

for name, schools in sorted(duplicates.items()):
    hc = hc_by_school[schools[0]]
    email = hc['email'].strip()

    # Try to identify correct school from email domain
    domain = email.split('@')[-1] if '@' in email else ''
    correct = DOMAIN_HINTS.get(domain)

    print(f"\n{name}")
    if correct:
        wrong = [s for s in sorted(schools) if s != correct]
        real  = [s for s in sorted(schools) if s == correct]
        print(f"  KEEP:       {real[0] if real else '?'} (email domain = {domain})")
        for w in wrong:
            print(f"  NEED HC:    {w}")
            needs_manual.append(w)
    else:
        print(f"  NO EMAIL — need to look up all:")
        for s in sorted(schools):
            print(f"              {s}")
            needs_manual.append(s)

print("\n" + "=" * 60)
print(f"Schools needing manual HC lookup: {len(needs_manual)}")
print("=" * 60)
for s in sorted(needs_manual):
    print(f"  {s}")
