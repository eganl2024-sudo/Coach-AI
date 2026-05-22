import sys
sys.path.insert(0, 'src')
import pandas as pd
from training_plan_generator import generate_training_plan

df = pd.read_csv('data/production/drill_library.csv', keep_default_na=False)
drills = df.to_dict('records')

profiles = [
    dict(name='Winger U15', position='Winger', secondary_position='None',
         level='Competitive Club', target_level='Academy/Select',
         sessions_per_week=3, session_duration=30,
         focus_areas=['1v1 Attacking', 'Weak Foot Development', 'Finishing & Shooting'],
         equipment_available=['Ball only', 'Cones'], created_date='2026-05-01'),
    dict(name='GK U13', position='Goalkeeper', secondary_position='None',
         level='Recreational', target_level='Competitive Club',
         sessions_per_week=2, session_duration=20,
         focus_areas=['First Touch', 'Speed & Agility'],
         equipment_available=['Ball only'], created_date='2026-05-01'),
    dict(name='CB U16 solo', position='Center Back', secondary_position='None',
         level='Competitive Club', target_level='Academy/Select',
         sessions_per_week=4, session_duration=45,
         focus_areas=['1v1 Defending', 'Passing & Combination Play', 'Positioning & Movement'],
         equipment_available=['Ball only', 'Cones'], created_date='2026-05-01'),
]

for p in profiles:
    plan = generate_training_plan(p, drills)
    sessions = plan.get('weeks', [{}])[0].get('sessions', [])
    print("Profile: {} | {} sessions".format(p['name'], len(sessions)))
    for s in sessions:
        d_list = s.get('drills', [])
        total = sum(x.get('allocated_time', 0) for x in d_list)
        names = [x.get('drill_name', '?')[:30] for x in d_list]
        blocks = [x.get('block_type', '?') for x in d_list]
        solo_flags = [str(x.get('solo_possible', '?')) for x in d_list]
        print("  S{} ({}min): {}".format(s['day_number'], total,
              list(zip(blocks, names, solo_flags))))
    print()
