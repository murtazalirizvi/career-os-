import re
from collections import Counter

with open('Frontend/index.html', encoding='utf-8') as f:
    content = f.read()

ids = re.findall(r'id="([^"]+)"', content)
dupes = {k: v for k, v in Counter(ids).items() if v > 1}
if dupes:
    print("DUPLICATE IDs FOUND:")
    for k, v in sorted(dupes.items()):
        print(f"  {v}x  {k}")
else:
    print("No duplicate IDs found.")
