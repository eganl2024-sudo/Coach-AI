import argparse
import csv
import os
import random
import re
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

# State to Region mapping
STATE_TO_REGION = {
    'ME': 'Northeast', 'NH': 'Northeast', 'VT': 'Northeast', 'MA': 'Northeast', 'RI': 'Northeast',
    'CT': 'Northeast', 'NY': 'Northeast', 'NJ': 'Northeast', 'PA': 'Northeast',
    'DE': 'Southeast', 'MD': 'Southeast', 'DC': 'Southeast', 'VA': 'Southeast', 'WV': 'Southeast',
    'NC': 'Southeast', 'SC': 'Southeast', 'GA': 'Southeast', 'FL': 'Southeast', 'KY': 'Southeast',
    'TN': 'Southeast', 'AL': 'Southeast', 'MS': 'Southeast',
    'OH': 'Midwest', 'IN': 'Midwest', 'IL': 'Midwest', 'MI': 'Midwest', 'WI': 'Midwest',
    'MN': 'Midwest', 'IA': 'Midwest', 'MO': 'Midwest', 'ND': 'Midwest', 'SD': 'Midwest',
    'NE': 'Midwest', 'KS': 'Midwest',
    'TX': 'Southwest', 'OK': 'Southwest', 'NM': 'Southwest', 'AZ': 'Southwest',
    'CO': 'West', 'UT': 'West', 'NV': 'West', 'WY': 'West', 'MT': 'West',
    'ID': 'West', 'WA': 'West', 'OR': 'West', 'CA': 'West', 'AK': 'West', 'HI': 'West'
}

# State name to abbreviation mapping
STATE_MAP = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC'
}

# Conference name abbreviations mapping
CONFERENCE_MAP = {
    "Atlantic Coast Conference": "ACC",
    "Big Ten Conference": "Big Ten",
    "Southeastern Conference": "SEC",
    "Big 12 Conference": "Big 12",
    "American Athletic Conference": "AAC",
    "Atlantic 10 Conference": "Atlantic 10",
    "Missouri Valley Conference": "MVC",
    "West Coast Conference": "WCC",
    "Western Athletic Conference": "WAC",
    "Patriot League": "Patriot",
    "Ivy League": "Ivy League",
    "Big East Conference": "Big East",
    "Big Sky Conference": "Big Sky",
    "Big West Conference": "Big West",
    "Horizon League": "Horizon",
    "Coastal Athletic Association": "CAA",
    "Southern Conference": "SoCon",
    "Sun Belt Conference": "Sun Belt",
    "Ohio Valley Conference": "OVC",
    "America East Conference": "America East",
    "Mid-American Conference": "MAC",
    "Northeast Conference": "NEC",
    "Metro Atlantic Athletic Conference": "MAAC",
    "Summit League": "Summit League",
    "Atlantic Sun Conference": "ASUN",
    "Southland Conference": "Southland",
    "Southwestern Athletic Conference": "SWAC"
}

# Regular expressions
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

# User agent generator
ua = UserAgent()

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def map_title(raw_title):
    raw_lower = raw_title.lower()
    
    # Check Director of Operations
    if "operations" in raw_lower and ("director" in raw_lower or "dir." in raw_lower or "dir" in raw_lower):
        return "Director of Operations"
        
    # Check Assistant Coach variants
    is_assistant_keywords = any(kw in raw_lower for kw in ["assistant", "associate", "co-head", "co head"])
    if is_assistant_keywords and "coach" in raw_lower:
        return "Assistant Coach"
        
    # Check Head Coach variants
    if "head" in raw_lower and "coach" in raw_lower:
        return "Head Coach"
        
    return None

def split_name(full_name):
    parts = full_name.split()
    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], " ".join(parts[1:])

def get_position_focus(text):
    text_lower = text.lower()
    if "gk" in text_lower or "goalkeeper" in text_lower or "goalkeeping" in text_lower:
        return "GK Coach"
    elif "defensive" in text_lower or "defense" in text_lower or "defender" in text_lower:
        return "Defensive"
    elif "attacking" in text_lower or "offense" in text_lower or "offensive" in text_lower or "forward" in text_lower:
        return "Attacking"
    return ""

def extract_email(element):
    for a in element.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            return a["href"].replace("mailto:", "").split("?")[0].strip()
    text = element.get_text()
    emails = re.findall(EMAIL_REGEX, text)
    if emails:
        return emails[0].strip()
    return ""

def extract_phone(element):
    for a in element.find_all("a", href=True):
        if a["href"].startswith("tel:"):
            return a["href"].replace("tel:", "").strip()
    text = element.get_text()
    phones = re.findall(PHONE_REGEX, text)
    if phones:
        return phones[0].strip()
    return ""

def extract_twitter(element):
    for a in element.find_all("a", href=True):
        href = a["href"].lower()
        if "twitter.com" in href or "x.com" in href:
            parsed = urlparse(a["href"])
            path = parsed.path.strip("/")
            if path and path not in ["intent", "share", "home", "search"]:
                return path.split("/")[0].replace("@", "").strip()
    return ""

def get_root_domain(url):
    if not url:
        return ""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return f"{parsed.scheme}://{netloc}"

def load_domain_map(csv_path):
    """Load school_name → athletics_domain.
    For women's domains_w.csv the key column is 'short_name'; for the men's
    domains.csv it is 'school_name'. Both are supported here.
    """
    domain_map = {}
    if not os.path.exists(csv_path):
        return domain_map
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('athletics_domain') and row['athletics_domain'].strip():
                # prefer short_name (women's mapping file) then school_name
                key = (row.get('short_name') or row.get('school_name') or '').strip()
                if key:
                    domain_map[key] = row['athletics_domain'].strip()
    return domain_map

def parse_coaches_page(url, dry_run=False):
    """Parses a coaching staff or roster page using unified selectors."""
    headers = {"User-Agent": ua.random}
    if dry_run:
        print(f"  Attempting URL: {url}")
        
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            if dry_run:
                print(f"    Failed: HTTP {resp.status_code}")
            return [], resp.status_code
            
        # Check if redirected to a generic index/homepage
        parsed_url = urlparse(resp.url)
        path_lower = parsed_url.path.lower()
        if path_lower in ["", "/", "/index.html", "/index.aspx", "/index.php"]:
            if dry_run:
                print("    Failed: Redirected to home page")
            return [], resp.status_code
            
        soup = BeautifulSoup(resp.content, "lxml")
    except Exception as e:
        if dry_run:
            print(f"    Error requesting page: {e}")
        return [], None

    coaches = []
    
    # --- Format 1: Table Layout (newer Sidearm format) ---
    tables = soup.find_all("table")
    for table in tables:
        headers_row = table.find("tr")
        if not headers_row:
            continue
        cols = [clean_text(th.get_text()).lower() for th in headers_row.find_all(["th", "td"])]
        
        if "name" in cols and ("title" in cols or "role" in cols or "position" in cols):
            rows = table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < len(cols):
                    continue
                
                coach_data = {}
                for idx, col in enumerate(cols):
                    if idx < len(cells):
                        coach_data[col] = cells[idx]
                
                name_cell = coach_data.get("name")
                title_cell = coach_data.get("title") or coach_data.get("role") or coach_data.get("position")
                if not name_cell or not title_cell:
                    continue
                
                raw_name = clean_text(name_cell.get_text())
                raw_title = clean_text(title_cell.get_text())
                
                mapped_title = map_title(raw_title)
                if not mapped_title:
                    continue
                
                first_name, last_name = split_name(raw_name)
                
                # Email
                email = ""
                email_cell = coach_data.get("email address") or coach_data.get("email")
                if email_cell:
                    email = extract_email(email_cell)
                if not email:
                    email = extract_email(row)
                    
                # Phone
                phone = ""
                phone_cell = coach_data.get("phone") or coach_data.get("phone number")
                if phone_cell:
                    phone = extract_phone(phone_cell)
                if not phone:
                    phone = extract_phone(row)
                    
                twitter = extract_twitter(row)
                focus = get_position_focus(raw_title + " " + row.get_text())
                
                coaches.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "title": mapped_title,
                    "email": email,
                    "phone": phone,
                    "position_focus": focus,
                    "twitter_handle": twitter
                })
            if coaches:
                return coaches, resp.status_code

    # --- Format 2: Card Layout (standard Sidearm format) ---
    cards = soup.find_all(class_=lambda c: c and "sidearm-staff-member" in c)
    for card in cards:
        name_el = card.find(class_=lambda c: c and "name" in c)
        title_el = card.find(class_=lambda c: c and ("title" in c or "role" in c))
        
        if not name_el or not title_el:
            continue
            
        raw_name = clean_text(name_el.get_text())
        raw_title = clean_text(title_el.get_text())
        
        mapped_title = map_title(raw_title)
        if not mapped_title:
            continue
            
        first_name, last_name = split_name(raw_name)
        email = extract_email(card)
        phone = extract_phone(card)
        twitter = extract_twitter(card)
        focus = get_position_focus(raw_title + " " + card.get_text())
        
        coaches.append({
            "first_name": first_name,
            "last_name": last_name,
            "title": mapped_title,
            "email": email,
            "phone": phone,
            "position_focus": focus,
            "twitter_handle": twitter
        })
    if coaches:
        return coaches, resp.status_code

    # --- Format 3: Roster-integrated Layout (Notre Dame format) ---
    staff_containers = soup.find_all(class_=lambda c: c and "staff" in c)
    for container in staff_containers:
        cards = container.find_all(class_=lambda c: c and ("player" in c or "inner" in c))
        if not cards:
            coach_links = container.find_all("a", href=lambda h: h and "/coach/" in h)
            cards = list(set([a.find_parent(class_=True) or a.parent for a in coach_links]))
            
        for card in cards:
            coach_a = card.find("a", href=lambda h: h and "/coach/" in h)
            if not coach_a:
                continue
            
            raw_name = clean_text(coach_a.get_text())
            if not raw_name:
                continue
                
            card_text = clean_text(card.get_text(separator="|"))
            parts = [p.strip() for p in card_text.split("|") if p.strip()]
            
            raw_title = ""
            for part in parts:
                if part != raw_name and map_title(part):
                    raw_title = part
                    break
            if not raw_title:
                for part in parts:
                    if part != raw_name and ("coach" in part.lower() or "director" in part.lower()):
                        raw_title = part
                        break
            
            mapped_title = map_title(raw_title)
            if not mapped_title:
                continue
                
            first_name, last_name = split_name(raw_name)
            email = extract_email(card)
            phone = extract_phone(card)
            twitter = extract_twitter(card)
            focus = get_position_focus(raw_title + " " + card.get_text())
            
            coaches.append({
                "first_name": first_name,
                "last_name": last_name,
                "title": mapped_title,
                "email": email,
                "phone": phone,
                "position_focus": focus,
                "twitter_handle": twitter
            })
            
    return coaches, resp.status_code

def main():
    parser = argparse.ArgumentParser(description="Scrape NCAA D1 Soccer Coaches.")
    parser.add_argument("--dry-run", action="store_true", help="Run a dry run on 3 programs only and print to console.")
    parser.add_argument("--gender", choices=["M", "W"], default="M", help="M = Men's (default), W = Women's")
    args = parser.parse_args()

    gender = args.gender

    # Determine script and output directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")

    # Gender-specific settings
    if gender == "W":
        wiki_list_url = "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_women%27s_soccer_programs"
        sport_paths = [
            "/sports/womens-soccer/coaches",
            "/sports/wsoc/coaches",
            "/sports/women-soccer/coaches",
            "/sports/w-soccer/coaches",
            "/sports/womens-soccer/roster",
            "/sports/wsoc/roster",
        ]
        programs_filename = "programs_w.csv"
        coaches_filename  = "coaches_w.csv"
        dry_run_targets   = [
            "University of North Carolina at Chapel Hill",
            "University of Portland",
            "Stanford University",
        ]
        label = "Women's"
    else:
        wiki_list_url = "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_men%27s_soccer_programs"
        sport_paths = [
            "/sports/mens-soccer/coaches",
            "/sports/msoc/coaches",
            "/sports/soccer/coaches",
            "/sports/mens-soccer/roster",
            "/sports/msoc/roster",
            "/sports/soccer/roster",
        ]
        programs_filename = "programs.csv"
        coaches_filename  = "coaches.csv"
        dry_run_targets   = [
            "University of Notre Dame",
            "University of California, Los Angeles",
            "University of North Carolina at Chapel Hill",
        ]
        label = "Men's"

    print(f"Fetching Division I {label} Soccer programs from Wikipedia...")
    headers = {"User-Agent": ua.random}
    resp = requests.get(wiki_list_url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch Wikipedia list (HTTP {resp.status_code}). Exiting.")
        return
        
    soup = BeautifulSoup(resp.content, "lxml")
    table = soup.find("table", class_="wikitable")
    if not table:
        print("Could not find the wikitable on Wikipedia list. Exiting.")
        return
        
    rows = table.find_all("tr")[1:]
    programs_to_scrape = []
    
    for r in rows:
        cells = r.find_all("td")
        if len(cells) < 6:
            continue
        
        # Institution name & link
        inst_cell = cells[0]
        inst_a = inst_cell.find("a")
        school_name = inst_a.text.strip() if inst_a else inst_cell.get_text(strip=True)
        school_wiki_path = inst_a["href"] if inst_a else ""
        
        # Nickname / Team page link
        nick_cell = cells[1]
        nick_a = nick_cell.find("a")
        team_wiki_path = nick_a["href"] if nick_a else ""
        
        # State
        raw_state = clean_text(cells[3].get_text())
        state_code = STATE_MAP.get(raw_state, "")
        region = STATE_TO_REGION.get(state_code, "")
        
        # Conference
        raw_conf = clean_text(cells[5].get_text())
        conference = CONFERENCE_MAP.get(raw_conf, raw_conf)
        
        programs_to_scrape.append({
            "school_name": school_name,
            "conference": conference,
            "state": state_code,
            "region": region,
            "division": "D1",
            "gender": gender,
            "school_wiki_url": "https://en.wikipedia.org" + school_wiki_path if school_wiki_path else "",
            "team_wiki_url": "https://en.wikipedia.org" + team_wiki_path if team_wiki_path else ""
        })

    print(f"Parsed {len(programs_to_scrape)} schools from Wikipedia.")

    # Load domain mapping (women's uses domains_w.csv keyed by short Wikipedia name)
    domains_file = "domains_w.csv" if gender == "W" else "domains.csv"
    csv_path = os.path.join(script_dir, "data", domains_file)
    domain_map = load_domain_map(csv_path)

    # Apply Dry Run filter if requested
    if args.dry_run:
        print("\n--- Running in DRY RUN mode ---")
        programs_to_scrape = [p for p in programs_to_scrape if p["school_name"] in dry_run_targets]
        print(f"Filtered to {len(programs_to_scrape)} target schools: {[p['school_name'] for p in programs_to_scrape]}\n")
    else:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        # Clear errors log
        with open(os.path.join(output_dir, "scrape_errors.log"), "w", encoding="utf-8") as f:
            f.write("=== Scraper Errors Log ===\n")

    successful_scrapes = 0
    failed_scrapes = 0
    all_programs_data = []
    all_coaches_data = []
    coach_dedup_set = set() # (school_name, first_name, last_name)

    for idx, prog in enumerate(programs_to_scrape):
        school = prog["school_name"]
        print(f"[{idx+1}/{len(programs_to_scrape)}] Processing: {school}")
        
        # Step 2: Resolve Domain from CSV
        domain = domain_map.get(school)
                    
        if not domain:
            err_msg = f"No domain in domains.csv for {school}"
            print(f"  Warning: {err_msg}")
            if not args.dry_run:
                with open(os.path.join(output_dir, "scrape_errors.log"), "a", encoding="utf-8") as f:
                    f.write(f"School: {school} | Error: {err_msg}\n")
            failed_scrapes += 1
            prog["program_url"] = ""
            prog["ncaa_id"] = ""
            if not args.dry_run:
                all_programs_data.append(prog)
            continue
            
        print(f"  Resolved Athletics Domain: {domain}")
        
        # Step 3: Scrape Coaching Staff Page
        coaches_found = []
        successful_path_url = ""
        paths_to_try = sport_paths
        
        last_attempted_url = ""
        for path in paths_to_try:
            url = domain + path
            last_attempted_url = url
            # Delay between coach page requests
            time.sleep(random.uniform(1.5, 3.5))
            
            parsed_coaches, status_code = parse_coaches_page(url, dry_run=args.dry_run)
            if parsed_coaches:
                coaches_found = parsed_coaches
                successful_path_url = url
                break
                
        if coaches_found:
            successful_scrapes += 1
            prog["program_url"] = successful_path_url
            prog["ncaa_id"] = "" # NCAA ID not found/empty
            
            if args.dry_run:
                print(f"  Successfully scraped coaches page: {successful_path_url}")
                print(f"  Coaches found ({len(coaches_found)}):")
                for coach in coaches_found:
                    print(f"    - {coach['first_name']} {coach['last_name']} ({coach['title']})")
                    print(f"      Email: {coach['email'] or 'N/A'} | Phone: {coach['phone'] or 'N/A'}")
                    print(f"      Twitter: {coach['twitter_handle'] or 'N/A'} | Focus: {coach['position_focus'] or 'N/A'}")
            else:
                all_programs_data.append(prog)
                for coach in coaches_found:
                    key = (school.strip(), coach["first_name"].strip(), coach["last_name"].strip())
                    if key not in coach_dedup_set:
                        coach_dedup_set.add(key)
                        all_coaches_data.append({
                            "school_name": school.strip(),
                            "first_name": coach["first_name"].strip(),
                            "last_name": coach["last_name"].strip(),
                            "title": coach["title"].strip(),
                            "email": coach["email"].strip(),
                            "phone": coach["phone"].strip(),
                            "position_focus": coach["position_focus"].strip(),
                            "twitter_handle": coach["twitter_handle"].strip(),
                            "source": "scrape"
                        })
        else:
            err_msg = f"Failed to scrape coaching staff page at {domain} (last URL tried: {last_attempted_url})"
            print(f"  Warning: {err_msg}")
            if not args.dry_run:
                with open(os.path.join(output_dir, "scrape_errors.log"), "a", encoding="utf-8") as f:
                    f.write(f"School: {school} | Tried: {last_attempted_url} | Error: Coaches not found or request failed\n")
            failed_scrapes += 1
            prog["program_url"] = ""
            prog["ncaa_id"] = ""
            if not args.dry_run:
                all_programs_data.append(prog)

    # 4. Write CSV Outputs if not in dry-run mode
    if not args.dry_run:
        # Write Programs CSV
        programs_file = os.path.join(output_dir, programs_filename)
        with open(programs_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["school_name", "conference", "region", "state", "division", "gender", "program_url", "ncaa_id"])
            writer.writeheader()
            for prog in all_programs_data:
                writer.writerow({
                    "school_name": prog["school_name"].strip(),
                    "conference": prog["conference"].strip(),
                    "region": prog["region"].strip(),
                    "state": prog["state"].strip(),
                    "division": prog["division"].strip(),
                    "gender": prog["gender"].strip(),
                    "program_url": prog["program_url"].strip(),
                    "ncaa_id": prog["ncaa_id"].strip()
                })

        # Write Coaches CSV
        coaches_file = os.path.join(output_dir, coaches_filename)
        with open(coaches_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["school_name", "first_name", "last_name", "title", "email", "phone", "position_focus", "twitter_handle", "source"])
            writer.writeheader()
            for coach in all_coaches_data:
                writer.writerow({k: v.strip() for k, v in coach.items()})

        print("\n=== Scraping Completed ===")
        print(f"Total programs attempted: {len(programs_to_scrape)}")
        print(f"Successfully scraped: {successful_scrapes}")
        print(f"Failed scrapes: {failed_scrapes}")
        print(f"Outputs written to: {output_dir}")
    else:
        print("\n=== Dry Run Completed ===")
        print(f"Dry run target schools attempted: {len(programs_to_scrape)}")
        print(f"Successfully scraped: {successful_scrapes}")
        print(f"Failed scrapes: {failed_scrapes}")
        print("Note: In dry run mode, no CSV files are written.")

if __name__ == "__main__":
    main()
