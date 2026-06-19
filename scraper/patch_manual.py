"""
patch_manual.py — writes manually researched coaches into coaches_enriched.csv.
Run after scrape_gaps.py --write.
"""

import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "output", "coaches_enriched.csv")

FIELDNAMES = ["school_name", "first_name", "last_name", "title", "email", "phone",
              "position_focus", "twitter_handle", "source"]

# ---------------------------------------------------------------------------
# All manually researched coaches
# ---------------------------------------------------------------------------
MANUAL_ADDITIONS = [
    # Old Dominion University
    {"school_name": "Old Dominion University",   "first_name": "Tennant", "last_name": "McVea",    "title": "Head Coach",      "email": "jmcvea@odu.edu",              "phone": ""},

    # Stanford University
    {"school_name": "Stanford University",        "first_name": "Jeremy",  "last_name": "Gunn",     "title": "Head Coach",      "email": "smsoccer@stanford.edu",       "phone": "650-643-7961"},
    {"school_name": "Stanford University",        "first_name": "Drew",    "last_name": "Hutchins", "title": "Assistant Coach", "email": "smsoccer@stanford.edu",       "phone": ""},

    # University of Pittsburgh
    {"school_name": "University of Pittsburgh",   "first_name": "Jay",     "last_name": "Vidovich", "title": "Head Coach",      "email": "msoccer@athletics.pitt.edu",  "phone": ""},

    # Virginia Polytechnic Institute and State University — handled by patch_vt.py

    # Liberty University — Scott Wells is current HC, Carl Reynolds is Associate HC
    {"school_name": "Liberty University", "first_name": "Scott", "last_name": "Wells",    "title": "Head Coach",      "email": "", "phone": "434-582-2000"},
    {"school_name": "Liberty University", "first_name": "Carl",  "last_name": "Reynolds", "title": "Assistant Coach", "email": "", "phone": "434-582-2000"},
    {"school_name": "Liberty University", "first_name": "Dylan", "last_name": "Lane",     "title": "Director of Operations", "email": "", "phone": ""},

    # San Diego State University
    {"school_name": "San Diego State University", "first_name": "Ryan",  "last_name": "Hopkins", "title": "Head Coach",      "email": "rhopkins2@sdsu.edu", "phone": ""},
    {"school_name": "San Diego State University", "first_name": "Jamie", "last_name": "Reid",    "title": "Assistant Coach", "email": "jreid2@sdsu.edu",    "phone": ""},
    {"school_name": "San Diego State University", "first_name": "David", "last_name": "Diaz",    "title": "Assistant Coach", "email": "dediaz@sdsu.edu",    "phone": ""},

    # University of Central Florida
    {"school_name": "University of Central Florida", "first_name": "Scott",  "last_name": "Calabrese", "title": "Head Coach",      "email": "soccer@athletics.ucf.edu",   "phone": ""},
    {"school_name": "University of Central Florida", "first_name": "Paul",   "last_name": "Souders",   "title": "Assistant Coach", "email": "soccer@athletics.ucf.edu",   "phone": ""},
    {"school_name": "University of Central Florida", "first_name": "Austin", "last_name": "Nyquist",   "title": "Assistant Coach", "email": "anyquist@athletics.ucf.edu", "phone": ""},

    # Central Connecticut State University
    {"school_name": "Central Connecticut State University", "first_name": "David",   "last_name": "Kelly",      "title": "Head Coach",      "email": "DKelly@ccsu.edu",              "phone": "(860) 832-3071"},
    {"school_name": "Central Connecticut State University", "first_name": "Andrew",  "last_name": "Sullivan",   "title": "Assistant Coach", "email": "Asullivan1@ccsu.edu",          "phone": ""},

    # Jacksonville University
    {"school_name": "Jacksonville University", "first_name": "Ali",     "last_name": "Simmons",   "title": "Head Coach",      "email": "asimmon17@ju.edu",            "phone": ""},
    {"school_name": "Jacksonville University", "first_name": "Thomas",  "last_name": "Buckner",   "title": "Assistant Coach", "email": "tbuckne@ju.edu",              "phone": "(904) 725-7420"},
    {"school_name": "Jacksonville University", "first_name": "Josh",    "last_name": "Moreira",   "title": "Assistant Coach", "email": "jmoreir@ju.edu",              "phone": ""},
    {"school_name": "Jacksonville University", "first_name": "Michael", "last_name": "Garrihy",   "title": "Assistant Coach", "email": "mgarrih@jacksonville.edu",    "phone": ""},

    # St. John's University (head coach missing from DB — assistants already there)
    {"school_name": "St. John's University", "first_name": "David", "last_name": "Masur",   "title": "Head Coach",      "email": "masurd@stjohns.edu",    "phone": ""},
    {"school_name": "St. John's University", "first_name": "David", "last_name": "Janezic", "title": "Assistant Coach", "email": "janezicd@stjohns.edu",  "phone": ""},

    # University of South Carolina
    {"school_name": "University of South Carolina", "first_name": "Tony",   "last_name": "Annan",      "title": "Head Coach",      "email": "SCMensSoccer@mailbox.sc.edu", "phone": ""},
    {"school_name": "University of South Carolina", "first_name": "Nat",    "last_name": "Hubert",     "title": "Assistant Coach", "email": "",                            "phone": ""},
    {"school_name": "University of South Carolina", "first_name": "Josh",   "last_name": "Bronstorph", "title": "Assistant Coach", "email": "",                            "phone": ""},
    {"school_name": "University of South Carolina", "first_name": "Jaxsen", "last_name": "Wirth",      "title": "Assistant Coach", "email": "",                            "phone": ""},

    # Bradley University
    {"school_name": "Bradley University", "first_name": "Tim",   "last_name": "Regan",   "title": "Head Coach",      "email": "tregan@fsmail.bradley.edu",   "phone": "309-677-2472"},
    {"school_name": "Bradley University", "first_name": "Brian", "last_name": "Barnett", "title": "Assistant Coach", "email": "bbarnett@fsmail.bradley.edu", "phone": "309-677-2472"},
    {"school_name": "Bradley University", "first_name": "John",  "last_name": "Trask",   "title": "Assistant Coach", "email": "jtrask@fsmail.bradley.edu",   "phone": ""},

    # George Mason University
    {"school_name": "George Mason University", "first_name": "Rich",  "last_name": "Costanzo",  "title": "Head Coach",      "email": "rcostanz@gmu.edu",  "phone": ""},
    {"school_name": "George Mason University", "first_name": "Noel",  "last_name": "Orozco",    "title": "Assistant Coach", "email": "norozco@gmu.edu",   "phone": ""},
    {"school_name": "George Mason University", "first_name": "Vahid", "last_name": "Talebloo",  "title": "Assistant Coach", "email": "",                  "phone": ""},

    # Queens University of Charlotte
    {"school_name": "Queens University of Charlotte", "first_name": "Oliver", "last_name": "Carias",   "title": "Head Coach",      "email": "cariaso@queens.edu",          "phone": "704-337-2530"},
    {"school_name": "Queens University of Charlotte", "first_name": "Omer",   "last_name": "Okyar",    "title": "Assistant Coach", "email": "okyaro@queens.edu",           "phone": ""},
    {"school_name": "Queens University of Charlotte", "first_name": "Alvaro", "last_name": "Anzola",   "title": "Assistant Coach", "email": "anzolazamudioa@queens.edu",   "phone": ""},
    {"school_name": "Queens University of Charlotte", "first_name": "Filipe", "last_name": "Mendonca", "title": "Assistant Coach", "email": "",                            "phone": ""},

    # Saint Peter's University
    {"school_name": "Saint Peter's University", "first_name": "Julian", "last_name": "Richens",  "title": "Head Coach",      "email": "jrichens@saintpeters.edu",   "phone": "201-761-7337"},
    {"school_name": "Saint Peter's University", "first_name": "Tom",    "last_name": "Coulson",  "title": "Assistant Coach", "email": "tcoulson17@saintpeters.edu", "phone": ""},
    {"school_name": "Saint Peter's University", "first_name": "Ferry",  "last_name": "Smedema",  "title": "Assistant Coach", "email": "fsmedema@saintpeters.edu",   "phone": ""},

    # Yale University
    {"school_name": "Yale University", "first_name": "Kylie",   "last_name": "Stannard", "title": "Head Coach",      "email": "kylie.stannard@yale.edu",    "phone": "203-432-1495"},
    {"school_name": "Yale University", "first_name": "Michael", "last_name": "Mordocco", "title": "Assistant Coach", "email": "michael.mordocco@yale.edu",  "phone": ""},
    {"school_name": "Yale University", "first_name": "Tyler",   "last_name": "Sheikh",   "title": "Assistant Coach", "email": "tyler.sheikh@yale.edu",      "phone": ""},
    {"school_name": "Yale University", "first_name": "Sean",    "last_name": "Kelly",    "title": "Assistant Coach", "email": "sean.d.kelly@yale.edu",      "phone": ""},
]

# ---------------------------------------------------------------------------
# Title updates for existing rows
# ---------------------------------------------------------------------------
TITLE_UPDATES = [
    # Tommy Moon: was scraped as Assistant Coach, now Interim Head Coach
    {"school_name": "Binghamton University", "first_name": "Tommy", "last_name": "Moon",
     "new_title": "Head Coach"},
]


def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} existing rows")

    # Apply title updates
    updated = 0
    for upd in TITLE_UPDATES:
        for row in rows:
            if (row["school_name"] == upd["school_name"]
                    and row["first_name"].lower() == upd["first_name"].lower()
                    and row["last_name"].lower() == upd["last_name"].lower()):
                old = row["title"]
                row["title"] = upd["new_title"]
                print(f"  Updated: {upd['first_name']} {upd['last_name']} ({upd['school_name']}): {old} -> {upd['new_title']}")
                updated += 1

    # Build dedup key set from existing rows
    existing_keys = {
        (r["school_name"].lower(), r["first_name"].lower(), r["last_name"].lower())
        for r in rows
    }

    # Add manual rows, skip dupes
    added = 0
    skipped = 0
    for entry in MANUAL_ADDITIONS:
        key = (entry["school_name"].lower(), entry["first_name"].lower(), entry["last_name"].lower())
        if key in existing_keys:
            print(f"  Skip (already exists): {entry['first_name']} {entry['last_name']} ({entry['school_name']})")
            skipped += 1
            continue
        row = {
            "school_name":    entry["school_name"],
            "first_name":     entry["first_name"],
            "last_name":      entry["last_name"],
            "title":          entry["title"],
            "email":          entry.get("email", ""),
            "phone":          entry.get("phone", ""),
            "position_focus": "",
            "twitter_handle": "",
            "source":         "manual",
        }
        rows.append(row)
        existing_keys.add(key)
        added += 1

    # Sort: school name, then head coach first, then last name
    rows.sort(key=lambda r: (
        r["school_name"],
        0 if r["title"] == "Head Coach" else 1,
        r["last_name"],
    ))

    with open(CSV_PATH, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone — {added} added, {updated} updated, {skipped} skipped")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    main()
