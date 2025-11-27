from pathlib import Path
lines = Path('pages/3_Practice_History.py').read_text(encoding='utf-8').splitlines()
print('len', len(lines))
for i,line in enumerate(lines,1):
    if 'star' in line or 'Intensity' in line or 'preview' in line:
        print(i, line.encode("unicode_escape").decode())
