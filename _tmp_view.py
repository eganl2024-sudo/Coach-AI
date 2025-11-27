from pathlib import Path
lines = Path('pages/3_Practice_History.py').read_text(encoding='utf-8').splitlines()
for i in range(235, 246):
    line = lines[i]
    print(i+1, line.encode('unicode_escape').decode())
