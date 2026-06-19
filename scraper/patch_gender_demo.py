"""Temporarily patch demo account athlete_profile gender to W for testing."""
import json, os, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from supabase import create_client

url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_KEY']
sb  = create_client(url, key)

username = sys.argv[1] if len(sys.argv) > 1 else 'demo'
gender   = sys.argv[2] if len(sys.argv) > 2 else 'W'

res = sb.table('user_data').select('data_value').eq('username', username).eq('data_key', 'athlete_profile').single().execute()
if not res.data:
    print(f"No athlete_profile found for '{username}'")
    sys.exit(1)

profile = json.loads(res.data['data_value'])
old_gender = profile.get('gender', 'not set')
profile['gender'] = gender

sb.table('user_data').update({'data_value': json.dumps(profile)}).eq('username', username).eq('data_key', 'athlete_profile').execute()
print(f"{username}: gender {old_gender} -> {gender}")
