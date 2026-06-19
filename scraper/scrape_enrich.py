import argparse
import csv
import os
import random
import re
import time
import urllib.parse
import collections
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

# Regex for email and phone numbers
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}'

# Generic email prefixes to demote/avoid
GENERIC_EMAIL_PREFIXES = {
    'athletics', 'msoccer', 'info', 'soccer', 'admissions', 'recruiting', 
    'media', 'sports', 'compliance', 'ticket', 'development', 'giving', 
    'marketing', 'operations', 'menssoccer', 'wsoccer', 'football', 
    'basketball', 'volleyball', 'baseball', 'softball', 'swim', 'track', 
    'crosscountry', 'tennis', 'golf', 'sid', 'athletic', 'recreation'
}

# User agent generator
ua = UserAgent()

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def get_root_domain(url):
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def extract_email_from_text(text):
    emails = re.findall(EMAIL_REGEX, text)
    return [e.strip() for e in emails]

def extract_phone_from_text(text):
    phones = re.findall(PHONE_REGEX, text)
    return [p.strip() for p in phones]


def score_bio_link(href, text, first_name, last_name):
    # Normalize names to lowercase alphanumeric for matching
    first_clean = re.sub(r'[^a-zA-Z0-9]', '', first_name).lower()
    last_clean = re.sub(r'[^a-zA-Z0-9]', '', last_name).lower()
    
    href_lower = href.lower()
    text_lower = text.lower()
    href_clean = re.sub(r'[^a-zA-Z0-9]', '', href_lower)
    text_clean = re.sub(r'[^a-zA-Z0-9]', '', text_lower)
    
    # Check if last name is in href or text (essential requirement)
    has_last_name = (last_clean in href_clean) or (last_clean in text_clean)
    if not has_last_name:
        return 0
        
    score = 5 # Base score for containing last name
    
    # Check if first name is in href or text
    if (first_clean in href_clean) or (first_clean in text_clean):
        score += 5
        
    # Check for typical bio patterns in href
    bio_keywords = ['/coach/', '/coaches/', '/staff/', '/bio/', '/bios/', '/profile/', '/profiles/', '/roster/']
    if any(kw in href_lower for kw in bio_keywords):
        score += 3
        
    return score

def find_bio_link(soup, program_url, first_name, last_name):
    best_link = None
    max_score = 0
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
            
        text = clean_text(a.get_text())
        score = score_bio_link(href, text, first_name, last_name)
        
        if score > max_score:
            max_score = score
            best_link = href
            
    # Require at least last name + (first name or bio path pattern)
    if best_link and max_score >= 8:
        return urllib.parse.urljoin(program_url, best_link)
    return None

def select_best_email(emails, coach_last_name):
    if not emails:
        return ""
        
    # Deduplicate while preserving order
    seen = set()
    deduped_emails = []
    for e in emails:
        e_lower = e.lower()
        if e_lower not in seen:
            seen.add(e_lower)
            deduped_emails.append(e)
            
    personal_emails = []
    generic_emails = []
    
    last_clean = re.sub(r'[^a-zA-Z0-9]', '', coach_last_name).lower()
    
    for email in deduped_emails:
        local_part = email.split('@')[0].lower()
        is_generic = False
        for prefix in GENERIC_EMAIL_PREFIXES:
            if local_part == prefix or local_part.startswith(prefix + '-') or local_part.startswith(prefix + '_'):
                is_generic = True
                break
        if is_generic:
            generic_emails.append(email)
        else:
            personal_emails.append(email)
            
    # Prefer personal emails, ordered by whether they contain the coach's last name
    if personal_emails:
        for email in personal_emails:
            local_part = email.split('@')[0].lower()
            if last_clean in local_part:
                return email
        return personal_emails[0]
        
    # Fallback to generic email if no personal emails are found
    if generic_emails:
        return generic_emails[0]
        
    return ""

def scrape_bio_page(url, coach_last_name):
    """Scrapes a coach's bio page and returns extracted (email, phone)."""
    headers = {"User-Agent": ua.random}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return "", ""
        soup = BeautifulSoup(resp.content, "lxml")
    except Exception:
        return "", ""
        
    # 1. Email Extraction
    emails = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            email_val = a["href"].replace("mailto:", "").split("?")[0].strip()
            if email_val:
                emails.append(email_val)
                
    # Fall back to regex search in page text
    emails.extend(extract_email_from_text(soup.get_text()))
    best_email = select_best_email(emails, coach_last_name)
    
    # 2. Phone Extraction
    phones = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("tel:"):
            phone_val = a["href"].replace("tel:", "").strip()
            if phone_val:
                phones.append(phone_val)
                
    # Fall back to regex search in page text
    phones.extend(extract_phone_from_text(soup.get_text()))
    best_phone = phones[0] if phones else ""
                
    return best_email, best_phone

def main():
    parser = argparse.ArgumentParser(description="Enrich NCAA D1 Soccer Coaches with emails/phones from bio pages.")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry run mode for 3 schools only and print to console.")
    parser.add_argument("--gender", choices=["M", "W"], default="M", help="M = Men's (default), W = Women's")
    args = parser.parse_args()

    gender = args.gender
    suffix = "_w" if gender == "W" else ""

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    programs_file        = os.path.join(script_dir, "output", f"programs{suffix}.csv")
    coaches_file         = os.path.join(script_dir, "output", f"coaches{suffix}.csv")
    output_enriched_file = os.path.join(script_dir, "output", f"coaches{suffix}_enriched.csv")
    log_file             = os.path.join(script_dir, "output", f"enrichment{suffix}_log.txt")

    if not os.path.exists(programs_file) or not os.path.exists(coaches_file):
        print(f"Error: {programs_file} or {coaches_file} not found. Run scrape_coaches.py --gender {gender} first.")
        return

    # Load programs map (school_name -> program_url)
    programs = {}
    with open(programs_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            programs[row["school_name"].strip()] = row["program_url"].strip()

    # Load coaches list
    coaches = []
    with open(coaches_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            coaches.append({k: v.strip() for k, v in row.items()})

    # Group coaches by school
    coaches_by_school = collections.defaultdict(list)
    for c in coaches:
        coaches_by_school[c["school_name"]].append(c)

    # Determine target schools
    if args.dry_run:
        target_schools = [
            "Butler University", 
            "Bryant University", 
            "Coastal Carolina University"
        ]
        print(f"\n--- Running in DRY RUN mode ---")
        print(f"Targeting: {target_schools}\n")
    else:
        # Step 1: Identify target schools (schools with zero emails OR missing head coach email)
        target_schools = []
        for school, school_coaches in coaches_by_school.items():
            has_no_emails = not any(c["email"].strip() for c in school_coaches)
            head_coach = next((c for c in school_coaches if c["title"] == "Head Coach"), None)
            missing_head_coach_email = head_coach and not head_coach["email"].strip()
            
            if has_no_emails or missing_head_coach_email:
                target_schools.append(school)
                
        print(f"Found {len(target_schools)} target schools for email/phone enrichment.")

    # Tracking metrics
    stats = {
        "target_schools_count": len(target_schools),
        "processed_schools_count": 0,
        "bio_pages_fetched": 0,
        "new_emails": 0,
        "new_phones": 0
    }

    # Cache for staff page BeautifulSoup to avoid duplicate fetches
    # (though typically one fetch per school is enough)
    school_soup_cache = {}

    for idx, school in enumerate(target_schools):
        print(f"[{idx+1}/{len(target_schools)}] Processing School: {school}")
        program_url = programs.get(school)
        if not program_url:
            print(f"  Warning: No program URL found for {school} in programs.csv")
            continue
            
        stats["processed_schools_count"] += 1
        
        # Re-fetch staff page
        print(f"  Re-fetching staff list: {program_url}")
        headers = {"User-Agent": ua.random}
        time.sleep(random.uniform(0.5, 1.0)) # overview fetch delay
        
        try:
            resp = requests.get(program_url, headers=headers, timeout=12)
            if resp.status_code != 200:
                print(f"  Warning: Failed to fetch overview page (HTTP {resp.status_code})")
                continue
            soup = BeautifulSoup(resp.content, "lxml")
        except Exception as e:
            print(f"  Warning: Error fetching overview page: {e}")
            continue

        # Find bios and scrape for each coach
        school_coaches = coaches_by_school.get(school, [])
        for coach in school_coaches:
            # Check if fields are empty
            has_email = bool(coach["email"].strip())
            has_phone = bool(coach["phone"].strip())
            
            # If both are already populated, skip
            if has_email and has_phone:
                continue
                
            first_name = coach["first_name"]
            last_name = coach["last_name"]
            
            print(f"  Looking for bio link of: {first_name} {last_name} ({coach['title']})")
            bio_url = find_bio_link(soup, program_url, first_name, last_name)
            
            if not bio_url:
                print("    Bio link NOT found.")
                continue
                
            print(f"    Found Bio Link: {bio_url}")
            
            # Delay between bio page requests
            time.sleep(random.uniform(1.5, 3.0))
            stats["bio_pages_fetched"] += 1
            
            email, phone = scrape_bio_page(bio_url, last_name)
            
            # Enrich fields only if they were blank
            updated = False
            if email and not has_email:
                coach["email"] = email
                stats["new_emails"] += 1
                updated = True
                print(f"    -> Extracted Email: {email}")
            if phone and not has_phone:
                coach["phone"] = phone
                stats["new_phones"] += 1
                updated = True
                print(f"    -> Extracted Phone: {phone}")
                
            if not updated:
                print("    -> No new information found on bio page.")

    # 4. Write CSV Outputs if not in dry-run mode
    if not args.dry_run:
        # Write Enriched Coaches CSV
        fieldnames = ["school_name", "first_name", "last_name", "title", "email", "phone", "position_focus", "twitter_handle", "source"]
        with open(output_enriched_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for coach in coaches:
                writer.writerow({k: coach[k] for k in fieldnames})
                
        # Count remaining schools with zero emails
        post_coaches_by_school = collections.defaultdict(list)
        for c in coaches:
            post_coaches_by_school[c["school_name"]].append(c)
            
        remaining_zero_email_schools = []
        for school, school_coaches in post_coaches_by_school.items():
            if not any(c["email"].strip() for c in school_coaches):
                remaining_zero_email_schools.append(school)
                
        remaining_zero_email_schools.sort()

        # Write Enrichment Log
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== Enrichment Summary ===\n")
            f.write(f"Target schools (zero emails/missing head coach): {stats['target_schools_count']}\n")
            f.write(f"Target schools processed: {stats['processed_schools_count']}\n")
            f.write(f"Bio pages fetched: {stats['bio_pages_fetched']}\n")
            f.write(f"New emails found: {stats['new_emails']}\n")
            f.write(f"New phones found: {stats['new_phones']}\n")
            f.write(f"Schools still with zero emails after enrichment: {len(remaining_zero_email_schools)}\n\n")
            f.write("=== Still Missing (schools with no emails after enrichment) ===\n")
            for s in remaining_zero_email_schools:
                f.write(f"- {s}\n")

        print("\n=== Enrichment Scraping Completed ===")
        print(f"New emails found: {stats['new_emails']}")
        print(f"New phones found: {stats['new_phones']}")
        print(f"Enriched outputs written to: {output_enriched_file}")
        print(f"Summary log written to: {log_file}")
    else:
        print("\n=== Dry Run Completed ===")
        print(f"Schools processed: {stats['processed_schools_count']}")
        print(f"Bio pages fetched: {stats['bio_pages_fetched']}")
        print(f"New emails found (dry-run): {stats['new_emails']}")
        print(f"New phones found (dry-run): {stats['new_phones']}")
        print("Note: In dry run mode, no files are written.")

if __name__ == "__main__":
    main()
