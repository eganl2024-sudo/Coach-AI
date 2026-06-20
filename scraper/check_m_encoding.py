import csv, os, re
from dotenv import load_dotenv
load_dotenv('../.env'); load_dotenv('../player-ai/.env.local')
from supabase import create_client

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

check = ['Gardner-Webb University', 'Rutgers University-New Brunswick',
         'University of Wisconsin-Madison', 'University of Wisconsin-Green Bay',
         'University of Wisconsin-Milwaukee', 'University of Missouri-Kansas City',
         'Long Island University']

for school in check:
    pid = slugify(school) + '-m'
    res = sb.table('coaches').select('coach_id', count='exact').eq('program_id', pid).execute()
    print(f"{school}: {res.count} coaches in Supabase (program_id={pid})")
