import csv, os, re
from dotenv import load_dotenv
load_dotenv('../.env'); load_dotenv('../player-ai/.env.local')
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

# Check programs table for Liberty
res = sb.table('programs').select('*').ilike('school_name', '%liberty%').execute()
print("Programs matching 'liberty':", [(r['program_id'], r['school_name'], r['gender']) for r in res.data])

# Check coaches_enriched.csv
coaches = list(csv.DictReader(open('output/coaches_enriched.csv', encoding='utf-8')))
lib_coaches = [c for c in coaches if 'liberty' in c['school_name'].lower()]
print("\nLiberty coaches in CSV:")
for c in lib_coaches:
    print(f"  {c['school_name']} | {c['first_name']} {c['last_name']} | {c['title']} | {c['email']}")

# Check Supabase coaches
res2 = sb.table('coaches').select('*').ilike('school_name', '%liberty%').execute()
print(f"\nLiberty coaches in Supabase ({len(res2.data)}):")
for r in res2.data:
    print(f"  {r['program_id']} | {r['first_name']} {r['last_name']} | {r['title']} | {r['email']}")
