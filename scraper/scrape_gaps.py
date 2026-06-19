"""
scrape_gaps.py — targeted gap filler for coaches_enriched.csv

Handles three classes of gaps:
  1. Programs with zero coaches (scraper tried /roster, should have tried /coaches or /staff)
  2. Programs with assistants but no head coach (Binghamton, St. John's)
  3. Coaches missing email — infer from the email pattern used by other coaches at same school

Usage:
  python scrape_gaps.py                  # dry run — shows what would be fetched
  python scrape_gaps.py --write          # write new rows into coaches_enriched.csv
  python scrape_gaps.py --infer-email    # also fill missing emails via pattern inference
"""

import argparse
import csv
import os
import re
import time
import random
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()

# ---------------------------------------------------------------------------
# Known athletics domains for the 20 missing programs + 2 head-coach gaps
# ---------------------------------------------------------------------------
TARGETS = {
    # 20 programs with zero coaches
    "Bradley University":                                "https://bradleybraves.com",
    "Central Connecticut State University":              "https://ccsubluedevils.com",
    "Clemson University":                                "https://clemsontigers.com",
    "George Mason University":                           "https://gomason.com",
    "Jacksonville University":                           "https://judolphins.prestosports.com",
    "Old Dominion University":                           "https://odusports.com",
    "Pennsylvania State University":                     "https://gopsusports.com",
    "Queens University of Charlotte":                    "https://queensathletics.com",
    "Saint Peter's University":                          "https://saintpeterspeacocks.com",
    "San Diego State University":                        "https://goaztecs.com",
    "San Jose State University":                         "https://sjsuspartans.com",
    "Seattle University":                                "https://goseattleu.com",
    "Stanford University":                               "https://gostanford.com",
    "University of California, Davis":                   "https://ucdavisaggies.com",
    "University of Central Florida":                     "https://ucfknights.com",
    "University of Pittsburgh":                          "https://pittsburghpanthers.com",
    "University of South Carolina":                      "https://gamecocksonline.com",
    "University of Virginia":                            "https://virginiasports.com",
    "Virginia Polytechnic Institute and State University": "https://hokiesports.com",
    "Yale University":                                   "https://yalebulldogs.com",
    # 2 programs that have assistants but no head coach
    "Binghamton University":                             "https://bubearcats.com",
    "St. John's University":                             "https://redstormsports.com",
}

# URL path patterns to try in order — coaches/staff pages before roster
URL_PATTERNS = [
    "/sports/mens-soccer/coaches",
    "/sports/m-soccer/coaches",
    "/sports/mens-soccer/staff",
    "/sports/m-soccer/staff",
    "/sports/soccer/coaches",
    "/sports/soccer/staff",
    "/sports/mens-soccer/roster",
    "/sports/m-soccer/roster",
    "/sports/soccer/roster",
]

FIELDNAMES = ["school_name", "first_name", "last_name", "title", "email", "phone",
              "position_focus", "twitter_handle", "source"]

# ---------------------------------------------------------------------------
# Shared parsing helpers (mirrors scrape_coaches.py)
# ---------------------------------------------------------------------------
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'


def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()


def map_title(raw):
    r = raw.lower()
    if "operations" in r and any(k in r for k in ("director", "dir")):
        return "Director of Operations"
    if any(k in r for k in ("assistant", "associate", "co-head")) and "coach" in r:
        return "Assistant Coach"
    if "head" in r and "coach" in r:
        return "Head Coach"
    return None


def split_name(full):
    parts = full.split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def get_position_focus(text):
    t = text.lower()
    if any(k in t for k in ("gk", "goalkeeper", "goalkeeping")):
        return "GK Coach"
    if any(k in t for k in ("defensive", "defense", "defender")):
        return "Defensive"
    if any(k in t for k in ("attacking", "offense", "offensive", "forward")):
        return "Attacking"
    return ""


def extract_email(el):
    for a in el.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            return a["href"].replace("mailto:", "").split("?")[0].strip()
    emails = re.findall(EMAIL_REGEX, el.get_text())
    return emails[0].strip() if emails else ""


def extract_phone(el):
    for a in el.find_all("a", href=True):
        if a["href"].startswith("tel:"):
            return a["href"].replace("tel:", "").strip()
    phones = re.findall(PHONE_REGEX, el.get_text())
    return phones[0].strip() if phones else ""


def extract_twitter(el):
    for a in el.find_all("a", href=True):
        href = a["href"].lower()
        if "twitter.com" in href or "x.com" in href:
            parsed = urlparse(a["href"])
            path = parsed.path.strip("/")
            if path and path not in ("intent", "share", "home", "search"):
                return path.split("/")[0].replace("@", "").strip()
    return ""


# ---------------------------------------------------------------------------
# Page fetcher + multi-format parser
# ---------------------------------------------------------------------------
def fetch(url):
    try:
        resp = requests.get(url, headers={"User-Agent": ua.random}, timeout=14)
        if resp.status_code != 200:
            return None, resp.status_code
        final_path = urlparse(resp.url).path.lower()
        if final_path in ("", "/", "/index.html", "/index.aspx", "/index.php"):
            return None, "redirected-home"
        return BeautifulSoup(resp.content, "lxml"), resp.status_code
    except Exception as e:
        return None, str(e)


def parse_coaches(soup):
    coaches = []

    # Format 1: table layout (newer Sidearm)
    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if not header_row:
            continue
        cols = [clean_text(th.get_text()).lower() for th in header_row.find_all(["th", "td"])]
        if "name" not in cols or not any(c in cols for c in ("title", "role", "position")):
            continue
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < len(cols):
                continue
            data = {cols[i]: cells[i] for i in range(min(len(cols), len(cells)))}
            name_el = data.get("name")
            title_el = data.get("title") or data.get("role") or data.get("position")
            if not name_el or not title_el:
                continue
            mapped = map_title(clean_text(title_el.get_text()))
            if not mapped:
                continue
            first, last = split_name(clean_text(name_el.get_text()))
            coaches.append({
                "first_name": first, "last_name": last, "title": mapped,
                "email": extract_email(data.get("email address") or data.get("email") or row),
                "phone": extract_phone(data.get("phone") or data.get("phone number") or row),
                "position_focus": get_position_focus(clean_text(title_el.get_text()) + " " + row.get_text()),
                "twitter_handle": extract_twitter(row),
            })
        if coaches:
            return coaches

    # Format 2: Sidearm card layout
    cards = soup.find_all(class_=lambda c: c and "sidearm-staff-member" in c)
    for card in cards:
        name_el = card.find(class_=lambda c: c and "name" in c)
        title_el = card.find(class_=lambda c: c and ("title" in c or "role" in c))
        if not name_el or not title_el:
            continue
        mapped = map_title(clean_text(title_el.get_text()))
        if not mapped:
            continue
        first, last = split_name(clean_text(name_el.get_text()))
        coaches.append({
            "first_name": first, "last_name": last, "title": mapped,
            "email": extract_email(card),
            "phone": extract_phone(card),
            "position_focus": get_position_focus(clean_text(title_el.get_text()) + " " + card.get_text()),
            "twitter_handle": extract_twitter(card),
        })
    if coaches:
        return coaches

    # Format 3: generic staff container with /coach/ links
    for container in soup.find_all(class_=lambda c: c and "staff" in c):
        links = container.find_all("a", href=lambda h: h and "/coach/" in h)
        parents = list({(a.find_parent(class_=True) or a.parent) for a in links})
        for card in parents:
            coach_a = card.find("a", href=lambda h: h and "/coach/" in h)
            if not coach_a:
                continue
            raw_name = clean_text(coach_a.get_text())
            if not raw_name:
                continue
            parts = [p.strip() for p in clean_text(card.get_text(separator="|")).split("|") if p.strip()]
            raw_title = next((p for p in parts if p != raw_name and map_title(p)), "")
            mapped = map_title(raw_title)
            if not mapped:
                continue
            first, last = split_name(raw_name)
            coaches.append({
                "first_name": first, "last_name": last, "title": mapped,
                "email": extract_email(card),
                "phone": extract_phone(card),
                "position_focus": get_position_focus(raw_title + " " + card.get_text()),
                "twitter_handle": extract_twitter(card),
            })
        if coaches:
            return coaches

    # Format 4: generic li/div blocks containing a coach name + title text
    for block in soup.find_all(["li", "div", "article"]):
        text = clean_text(block.get_text())
        mapped = map_title(text)
        if not mapped:
            continue
        # Must have a name-looking string (two capitalised words)
        name_match = re.search(r'\b([A-Z][a-z]+)\s+([A-Z][a-z\-]+)\b', text)
        if not name_match:
            continue
        # Skip if block is too large (probably a whole section, not a single coach)
        if len(text) > 400:
            continue
        first, last = name_match.group(1), name_match.group(2)
        coaches.append({
            "first_name": first, "last_name": last, "title": mapped,
            "email": extract_email(block),
            "phone": extract_phone(block),
            "position_focus": get_position_focus(text),
            "twitter_handle": extract_twitter(block),
        })

    # Deduplicate by (first, last)
    seen = set()
    unique = []
    for c in coaches:
        key = (c["first_name"].lower(), c["last_name"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


MAX_SOCCER_STAFF = 12  # typical D1 soccer program has 3-6; >12 = probably all-sports page

def scrape_school(school_name, domain, existing_names=None):
    """Try each URL pattern until one returns a plausible soccer staff list."""
    existing_names = existing_names or set()
    best = None  # (coaches, new, url) — fallback if nothing clean found
    for pattern in URL_PATTERNS:
        url = domain.rstrip("/") + pattern
        print(f"  Trying {url} ...", end=" ")
        soup, status = fetch(url)
        if soup is None:
            print(f"skipped ({status})")
            time.sleep(random.uniform(0.5, 1.2))
            continue
        coaches = parse_coaches(soup)
        if not coaches:
            print("no coaches parsed")
            time.sleep(random.uniform(0.8, 1.5))
            continue
        if len(coaches) > MAX_SOCCER_STAFF:
            print(f"skipped ({len(coaches)} coaches — likely all-sports page, needs manual review)")
            time.sleep(random.uniform(0.8, 1.5))
            if best is None:
                new = [c for c in coaches
                       if (c["first_name"].lower(), c["last_name"].lower()) not in existing_names]
                best = (coaches, new, url)
            continue
        new = [c for c in coaches
               if (c["first_name"].lower(), c["last_name"].lower()) not in existing_names]
        print(f"found {len(coaches)} coaches ({len(new)} new)")
        time.sleep(random.uniform(1.0, 2.0))
        return coaches, new, False  # False = not a warning result
    if best:
        print(f"  NEEDS MANUAL REVIEW: only found {len(best[0])} coaches via {best[2]} (may be all-sports)")
        return best[0], best[1], True  # True = warning, skip in --write unless --include-warnings
    return [], [], False


# ---------------------------------------------------------------------------
# Email pattern inference
# ---------------------------------------------------------------------------
def infer_email_pattern(emails, domain):
    """
    Given a list of known emails at a school, detect the format:
      firstinitiallastname@domain  -> {f}{last}
      first.last@domain            -> {first}.{last}
      firstlast@domain             -> {first}{last}
      flast@domain                 -> {f}{last}  (same as first)
    Returns a format string with {first}, {last}, {f} tokens.
    """
    if not emails or not domain:
        return None
    patterns = []
    for email in emails:
        local = email.split("@")[0].lower()
        for coach_email in emails:
            if coach_email == email:
                continue
        # We need name info to reverse-engineer — handled in caller
    return None  # placeholder; real inference below


def detect_school_email_pattern(rows):
    """
    Given all coach rows for a school that HAVE emails, detect the naming pattern.
    Returns callable(first, last) -> email_local or None.
    """
    if not rows:
        return None

    domain = None
    samples = []
    for r in rows:
        if not r.get("email") or "@" not in r["email"]:
            continue
        local, d = r["email"].lower().split("@", 1)
        domain = d
        first = r["first_name"].lower().strip()
        last = r["last_name"].lower().strip()
        if not first or not last:
            continue
        samples.append((first, last, local))

    if not samples or not domain:
        return None

    # Test each pattern against all samples — pick the one that matches most
    f, l, loc = samples[0]
    fi = f[0] if f else ""

    candidates = {
        "{f}{last}": lambda first, last: first[0] + last,
        "{first}.{last}": lambda first, last: first + "." + last,
        "{first}{last}": lambda first, last: first + last,
        "{first}_{last}": lambda first, last: first + "_" + last,
        "{first}": lambda first, last: first,
        "{last}": lambda first, last: last,
        "{last}{f}": lambda first, last: last + first[0],
    }

    best_pattern = None
    best_score = 0
    for name, fn in candidates.items():
        score = sum(1 for first, last, local in samples if fn(first, last) == local)
        if score > best_score:
            best_score = score
            best_pattern = fn

    # Only use if pattern matches at least half the samples
    if best_score < max(1, len(samples) // 2):
        return None

    return best_pattern, domain


def infer_missing_emails(all_rows):
    """Fill in email field for rows missing email using detected school pattern."""
    from collections import defaultdict

    by_school = defaultdict(list)
    for r in all_rows:
        by_school[r["school_name"]].append(r)

    filled = 0
    for school, rows in by_school.items():
        has_email = [r for r in rows if r.get("email")]
        no_email = [r for r in rows if not r.get("email")]
        if not no_email or not has_email:
            continue
        result = detect_school_email_pattern(has_email)
        if not result:
            continue
        pattern_fn, domain = result
        for r in no_email:
            first = r["first_name"].lower().strip()
            last = r["last_name"].lower().strip()
            if not first or not last:
                continue
            inferred = pattern_fn(first, last) + "@" + domain
            r["email"] = inferred
            filled += 1

    print(f"\nEmail inference: filled {filled} missing emails")
    return all_rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write results into coaches_enriched.csv")
    parser.add_argument("--infer-email", action="store_true", help="Fill missing emails via pattern inference")
    parser.add_argument("--include-warnings", action="store_true",
                        help="Also write schools flagged as needing manual review (all-sports page fallbacks)")
    args = parser.parse_args()

    csv_path = os.path.join(os.path.dirname(__file__), "output", "coaches_enriched.csv")

    # Load existing data
    existing = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        existing = list(csv.DictReader(f))

    existing_schools = {r["school_name"] for r in existing}
    schools_with_head = {r["school_name"] for r in existing if r["title"] == "Head Coach"}

    print(f"Loaded {len(existing)} existing coaches from {len(existing_schools)} schools\n")

    new_rows = []

    for school_name, domain in TARGETS.items():
        is_gap_school = school_name not in existing_schools
        needs_head = school_name not in schools_with_head and school_name in existing_schools

        if not is_gap_school and not needs_head:
            print(f"SKIP  {school_name} (already has coaches + head coach)")
            continue

        label = "MISSING" if is_gap_school else "NO-HEAD"
        print(f"\n[{label}] {school_name}")

        # Build set of existing coach names for this school (for dedup on head-coach-gap schools)
        existing_names = {
            (r["first_name"].lower(), r["last_name"].lower())
            for r in existing if r["school_name"] == school_name
        }

        all_coaches, new_coaches, is_warning = scrape_school(school_name, domain, existing_names)

        if not all_coaches:
            print(f"  ->Could not scrape {school_name}")
            continue

        if is_warning and not args.include_warnings:
            print(f"  ->Skipping (needs manual review — run with --include-warnings to force)")
            continue

        if is_gap_school:
            for c in all_coaches:
                new_rows.append({**c, "school_name": school_name, "source": "gap_scrape"})
            print(f"  ->Adding {len(all_coaches)} coaches{' [WARNING: review manually]' if is_warning else ''}")
        else:
            head_coaches = [c for c in new_coaches if c["title"] == "Head Coach"]
            for c in head_coaches:
                new_rows.append({**c, "school_name": school_name, "source": "gap_scrape"})
            print(f"  ->Adding {len(head_coaches)} new head coach(es){' [WARNING: review manually]' if is_warning else ''}")

    print(f"\n{'='*60}")
    print(f"Found {len(new_rows)} new coach rows across {len(TARGETS)} targeted schools")

    if args.infer_email:
        all_rows = existing + new_rows
        all_rows = infer_missing_emails(all_rows)
        # Separate back out
        existing_keys = {(r["school_name"], r["first_name"], r["last_name"]) for r in existing}
        new_rows = [r for r in all_rows if (r["school_name"], r["first_name"], r["last_name"]) not in existing_keys]

    if not args.write:
        print("\nDry run — pass --write to update coaches_enriched.csv")
        print("New rows preview:")
        for r in new_rows[:10]:
            print(f"  {r['school_name']} | {r['first_name']} {r['last_name']} | {r['title']} | {r.get('email','')}")
        if len(new_rows) > 10:
            print(f"  ... and {len(new_rows)-10} more")
        return

    # Write — append new rows then rewrite entire file sorted by school
    all_rows = existing + new_rows
    all_rows.sort(key=lambda r: (r["school_name"], r["title"] != "Head Coach", r["last_name"]))

    # If infer-email ran, all_rows already has the filled emails merged in
    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} total coaches to {csv_path}")
    print(f"Added {len(new_rows)} new rows")


if __name__ == "__main__":
    main()
