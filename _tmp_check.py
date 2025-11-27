from pathlib import Path
lines = Path('pages/3_Practice_History.py').read_text(encoding='utf-8').splitlines()
start = end = None
for i, l in enumerate(lines):
    if start is None and l.strip() == 'st.subheader("Timeline")':
        start = i
    if start is not None and end is None and l.strip() == 'st.divider()' and i + 1 < len(lines) and lines[i+1].lstrip().startswith('if is_dev'):
        end = i
print(start, end)
