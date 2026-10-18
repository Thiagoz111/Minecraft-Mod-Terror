"""Dev-only: rebuilds screenshots from a saved CI log (see shots.py)."""
import base64
import os
import re
import sys

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
text = open(src, encoding='utf-8', errors='replace').read()
text = text.replace('\\n', '\n')
name, buf, n = None, [], 0
for line in text.splitlines():
    line = re.sub(r'^\S*\d{4}-\d\d-\d\dT[\d:.]+Z ', '', line)
    if line.startswith('=== SHOT '):
        name, buf = line.split()[2], []
    elif line.startswith('B64:') and name:
        buf.append(line[4:].strip())
    elif line.startswith('=== ENDSHOT') and name:
        open(os.path.join(out, name + '.jpg'), 'wb').write(base64.b64decode(''.join(buf)))
        n += 1
        name = None
print('decoded', n)
