from pathlib import Path
lines = Path('pages/3_Practice_History.py').read_text(encoding='utf-8').splitlines()
for i in range(378, 406):
    print(i+1, lines[i].encode('unicode_escape').decode())
