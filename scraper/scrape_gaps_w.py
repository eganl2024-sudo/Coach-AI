"""
scrape_gaps_w.py — Re-scrapes women's programs that failed in the main run.

Reads the error log to identify failed schools, tries extended URL paths,
and appends new coaches to coaches_w.csv / updates programs_w.csv program_url.

Usage:
    python scrape_gaps_w.py          # try all failed schools
    python scrape_gaps_w.py --dry-run  # print what would be tried
"""

import argparse
import csv
import os
import random
import re
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, 'output')
ERRORS_LOG  = os.path.join(OUTPUT_DIR, 'scrape_errors.log')
PROGRAMS_W  = os.path.join(OUTPUT_DIR, 'programs_w.csv')
COACHES_W   = os.path.join(OUTPUT_DIR, 'coaches_w.csv')
DOMAINS_W   = os.path.join(SCRIPT_DIR, 'data', 'domains_w.csv')

ua = UserAgent()

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

# Extended path list — all known women's soccer URL patterns across Sidearm, CBS, etc.
PATHS_TO_TRY = [
    "/sports/womens-soccer/coaches",
    "/sports/wsoc/coaches",
    "/sports/women-soccer/coaches",
    "/sports/w-soccer/coaches",
    "/sports/soccer/coaches",          # some schools share path
    "/sports/womens-soccer/roster",
    "/sports/wsoc/roster",
    "/sports/women-soccer/roster",
    "/sports/w-soccer/roster",
    "/sports/soccer/roster",
    "/womens-soccer/coaches",
    "/womens-soccer/roster",
    "/wsoc/coaches",
    "/wsoc/roster",
]


def clean_text(text):
    if not text:
        return ""
    text = text.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def map_title(raw_title):
    raw_lower = raw_title.lower()
    if "operations" in raw_lower and ("director" in raw_lower or "dir" in raw_lower):
        return "Director of Operations"
    if any(kw in raw_lower for kw in ["assistant", "associate", "co-head"]) and "coach" in raw_lower:
        return "Assistant Coach"
    if "head" in raw_lower and "coach" in raw_lower:
        return "Head Coach"
    return None


def split_name(full_name):
    parts = full_name.split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def extract_email(element):
    for a in element.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            return a["href"].replace("mailto:", "").split("?")[0].strip()
    emails = re.findall(EMAIL_REGEX, element.get_text())
    return emails[0].strip() if emails else ""


def parse_coaches_page(url):
    headers = {"User-Agent": ua.random}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return [], resp.status_code
        from urllib.parse import urlparse
        path = urlparse(resp.url).path.lower()
        if path in ["", "/", "/index.html", "/index.aspx"]:
            return [], resp.status_code
        soup = BeautifulSoup(resp.content, "lxml")
    except Exception:
        return [], None

    coaches = []

    # Table layout
    for table in soup.find_all("table"):
        hr = table.find("tr")
        if not hr:
            continue
        cols = [clean_text(th.get_text()).lower() for th in hr.find_all(["th", "td"])]
        if "name" in cols and any(c in cols for c in ["title", "role", "position"]):
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                cd = {cols[i]: cells[i] for i in range(min(len(cols), len(cells)))}
                name_el = cd.get("name")
                title_el = cd.get("title") or cd.get("role") or cd.get("position")
                if not name_el or not title_el:
                    continue
                title = map_title(clean_text(title_el.get_text()))
                if not title:
                    continue
                first, last = split_name(clean_text(name_el.get_text()))
                coaches.append({"first_name": first, "last_name": last, "title": title,
                                 "email": extract_email(row), "phone": "", "position_focus": "",
                                 "twitter_handle": "", "source": "scrape"})
            if coaches:
                return coaches, resp.status_code

    # Card layout
    for card in soup.find_all(class_=lambda c: c and "sidearm-staff-member" in c):
        name_el = card.find(class_=lambda c: c and "name" in c)
        title_el = card.find(class_=lambda c: c and ("title" in c or "role" in c))
        if not name_el or not title_el:
            continue
        title = map_title(clean_text(title_el.get_text()))
        if not title:
            continue
        first, last = split_name(clean_text(name_el.get_text()))
        coaches.append({"first_name": first, "last_name": last, "title": title,
                         "email": extract_email(card), "phone": "", "position_focus": "",
                         "twitter_handle": "", "source": "scrape"})
    return coaches, resp.status_code


def load_domain_map():
    dm = {}
    with open(DOMAINS_W, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            key = (r.get('short_name') or r.get('school_name') or '').strip()
            dom = r.get('athletics_domain', '').strip()
            if key and dom:
                dm[key] = dom
    return dm


def load_failed_schools():
    """Parse the error log and return list of school names that failed."""
    if not os.path.exists(ERRORS_LOG):
        return []
    failed = []
    with open(ERRORS_LOG, encoding='utf-8') as f:
        for line in f:
            m = re.match(r"^School: (.+?) \|", line)
            if m:
                failed.append(m.group(1).strip())
    return failed


def load_existing_coaches():
    """Return set of (school_name, first_name, last_name) already in coaches_w.csv."""
    existing = set()
    if not os.path.exists(COACHES_W):
        return existing
    with open(COACHES_W, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            existing.add((r['school_name'].strip(), r['first_name'].strip(), r['last_name'].strip()))
    return existing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    failed = load_failed_schools()
    if not failed:
        print("No failed schools found in error log.")
        return

    # Deduplicate (same school may appear multiple times in log)
    failed = list(dict.fromkeys(failed))
    print(f"Retrying {len(failed)} failed schools...")

    domain_map = load_domain_map()
    existing = load_existing_coaches()

    new_coaches = []
    still_failed = []
    updated_programs = []

    for school in failed:
        domain = domain_map.get(school)
        if not domain:
            print(f"  SKIP (no domain): {school}")
            still_failed.append(school)
            continue

        print(f"  Retrying: {school} ({domain})")
        if args.dry_run:
            print(f"    Would try {len(PATHS_TO_TRY)} paths")
            continue

        found = []
        success_url = ""
        for path in PATHS_TO_TRY:
            url = domain + path
            time.sleep(random.uniform(1.0, 2.5))
            coaches, _ = parse_coaches_page(url)
            if coaches:
                found = coaches
                success_url = url
                break

        if found:
            print(f"    Found {len(found)} coaches at {success_url}")
            updated_programs.append((school, success_url))
            for c in found:
                key = (school, c['first_name'], c['last_name'])
                if key not in existing:
                    existing.add(key)
                    new_coaches.append({**c, 'school_name': school})
        else:
            print(f"    Still failed: {school}")
            still_failed.append(school)

    if args.dry_run:
        return

    # Append new coaches to coaches_w.csv
    if new_coaches:
        fieldnames = ["school_name", "first_name", "last_name", "title", "email",
                      "phone", "position_focus", "twitter_handle", "source"]
        with open(COACHES_W, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for c in new_coaches:
                writer.writerow({k: c.get(k, '').strip() for k in fieldnames})
        print(f"\nAdded {len(new_coaches)} new coaches to {COACHES_W}")

    # Update program_url in programs_w.csv for recovered schools
    if updated_programs:
        url_updates = {school: url for school, url in updated_programs}
        rows = []
        with open(PROGRAMS_W, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['school_name'] in url_updates and not r.get('program_url'):
                    r['program_url'] = url_updates[r['school_name']]
                rows.append(r)
        with open(PROGRAMS_W, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated program_url for {len(updated_programs)} schools")

    print(f"\nSummary:")
    print(f"  Recovered: {len(failed) - len(still_failed)}")
    print(f"  Still failing: {len(still_failed)}")
    if still_failed:
        print("  Remaining failures:")
        for s in still_failed:
            print(f"    - {s}")


if __name__ == '__main__':
    main()
