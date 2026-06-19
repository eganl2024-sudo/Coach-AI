"""
build_domains_w.py — maps women's Wikipedia short names to domains.csv full names.

Reads:  output/programs_w.csv  (short names from women's Wikipedia)
        data/domains.csv        (full institutional names → athletics domains)

Writes: data/domains_w.csv     (short_name, school_name, athletics_domain)
        output/domains_w_unmatched.txt  (names that need manual mapping)

Run:    python build_domains_w.py
Then review domains_w_unmatched.txt and add manual entries to
data/domains_w_manual.csv (same columns: short_name, athletics_domain)
"""

import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PROGRAMS_W   = os.path.join(SCRIPT_DIR, 'output', 'programs_w.csv')
DOMAINS_CSV  = os.path.join(SCRIPT_DIR, 'data',   'domains.csv')
OUT_CSV      = os.path.join(SCRIPT_DIR, 'data',   'domains_w.csv')
UNMATCHED    = os.path.join(SCRIPT_DIR, 'output', 'domains_w_unmatched.txt')
MANUAL_CSV   = os.path.join(SCRIPT_DIR, 'data',   'domains_w_manual.csv')


def normalize(name: str) -> str:
    """Strip common prefixes/suffixes and lowercase for fuzzy matching."""
    n = name.lower()
    for prefix in ['university of ', 'the university of ', 'university at ',
                   'college of ', 'the college of ', 'the ']:
        if n.startswith(prefix):
            n = n[len(prefix):]
    for suffix in [', the', ' university', ' college', ' state',
                   ', suny', ' a&m', ' polytechnic', ' tech']:
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    # Remove punctuation
    n = re.sub(r'[^a-z0-9 ]', '', n).strip()
    # Collapse spaces
    n = re.sub(r'\s+', ' ', n)
    return n


def token_overlap(a: str, b: str) -> float:
    ta = set(normalize(a).split())
    tb = set(normalize(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def main():
    # Load domains: full_name → domain
    domains: list[tuple[str, str]] = []
    with open(DOMAINS_CSV, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            sn = r['school_name'].strip()
            dom = r.get('athletics_domain', '').strip()
            if sn and dom:
                domains.append((sn, dom))

    # Load manual overrides if they exist
    manual: dict[str, str] = {}   # short_name (lower) → domain
    if os.path.exists(MANUAL_CSV):
        with open(MANUAL_CSV, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                k = r['short_name'].strip().lower()
                v = r['athletics_domain'].strip()
                if k and v:
                    manual[k] = v

    # Load women's school short names
    women_names: list[str] = []
    with open(PROGRAMS_W, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            sn = r['school_name'].strip()
            if sn:
                women_names.append(sn)

    matched:   list[tuple[str, str, str]] = []   # short_name, full_name, domain
    unmatched: list[str] = []

    for short in women_names:
        short_lower = short.lower()

        # 1. Manual override
        if short_lower in manual:
            matched.append((short, short, manual[short_lower]))
            continue

        # 2. Exact match (case-insensitive)
        exact = next((d for d in domains if d[0].lower() == short_lower), None)
        if exact:
            matched.append((short, exact[0], exact[1]))
            continue

        # 3. Exact normalized match
        norm_short = normalize(short)
        norm_match = next((d for d in domains if normalize(d[0]) == norm_short), None)
        if norm_match:
            matched.append((short, norm_match[0], norm_match[1]))
            continue

        # 4. One contains the other (normalized)
        contains = [d for d in domains
                    if norm_short in normalize(d[0]) or normalize(d[0]) in norm_short]
        if len(contains) == 1:
            matched.append((short, contains[0][0], contains[0][1]))
            continue

        # 5. Token overlap ≥ 0.6
        scored = sorted(domains, key=lambda d: token_overlap(short, d[0]), reverse=True)
        if scored and token_overlap(short, scored[0][0]) >= 0.6:
            matched.append((short, scored[0][0], scored[0][1]))
            continue

        unmatched.append(short)

    # Write domains_w.csv
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['short_name', 'school_name', 'athletics_domain'])
        writer.writeheader()
        for short, full, dom in matched:
            writer.writerow({'short_name': short, 'school_name': full, 'athletics_domain': dom})

    # Write unmatched
    with open(UNMATCHED, 'w', encoding='utf-8') as f:
        f.write(f"# {len(unmatched)} schools not matched — add to data/domains_w_manual.csv\n")
        f.write("# Format of that file: short_name,athletics_domain\n\n")
        for name in sorted(unmatched):
            f.write(name + '\n')

    print(f"Matched:   {len(matched)} / {len(women_names)}")
    print(f"Unmatched: {len(unmatched)}")
    print(f"Written:   {OUT_CSV}")
    if unmatched:
        print(f"Review:    {UNMATCHED}")


if __name__ == '__main__':
    main()
