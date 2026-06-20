import csv
from collections import defaultdict

coaches = list(csv.DictReader(open('output/coaches_w_enriched.csv', encoding='utf-8')))
programs = list(csv.DictReader(open('output/programs_w.csv', encoding='utf-8')))

schools_with_coaches = set(c['school_name'] for c in coaches)
all_programs = set(p['school_name'] for p in programs)
zero_coaches = sorted(all_programs - schools_with_coaches)

schools = defaultdict(lambda: {'head': None, 'assistants': 0, 'has_email': 0, 'total': 0})
for c in coaches:
    s = c['school_name']
    schools[s]['total'] += 1
    if c['title'] == 'Head Coach':
        schools[s]['head'] = c
    else:
        schools[s]['assistants'] += 1
    if c['email'].strip():
        schools[s]['has_email'] += 1

no_head        = [(s, d) for s, d in schools.items() if not d['head']]
head_no_email  = [(s, d) for s, d in schools.items() if d['head'] and not d['head']['email'].strip()]
no_staff       = [(s, d) for s, d in schools.items() if d['head'] and d['assistants'] == 0]

# Duplicate head coach names across schools (likely scraper errors)
hc_names = defaultdict(list)
for s, d in schools.items():
    if d['head']:
        name = f"{d['head']['first_name']} {d['head']['last_name']}"
        hc_names[name].append(s)
duplicates = {n: ss for n, ss in hc_names.items() if len(ss) > 1}

print("=" * 60)
print("WOMEN'S D1 DATA AUDIT")
print("=" * 60)
print(f"Total programs:            {len(all_programs)}")
print(f"Programs with coaches:     {len(schools_with_coaches)}")
print(f"Programs with ZERO coaches:{len(zero_coaches)}")
print(f"Head coach present:        {sum(1 for d in schools.values() if d['head'])}")
print(f"  with email:              {sum(1 for d in schools.values() if d['head'] and d['head']['email'].strip())}")
print(f"  missing email:           {len(head_no_email)}")
print(f"No head coach tagged:      {len(no_head)}")
print(f"Head only, no assistants:  {len(no_staff)}")

print()
print("--- HEAD COACH MISSING EMAIL (fix these) ---")
for s, d in sorted(head_no_email):
    hc = d['head']
    print(f"  {s}: {hc['first_name']} {hc['last_name']}")

print()
print("--- NO HEAD COACH TAGGED ---")
for s, d in sorted(no_head):
    print(f"  {s}  ({d['total']} staff, {d['has_email']} with email)")

print()
print("--- SUSPICIOUS: same head coach name at multiple schools ---")
for name, school_list in sorted(duplicates.items()):
    print(f"  {name}: {', '.join(sorted(school_list))}")

print()
print("--- ZERO COACHES (37 schools) ---")
for s in zero_coaches:
    conf = next((p['conference'] for p in programs if p['school_name'] == s), '?')
    print(f"  {s} ({conf})")
