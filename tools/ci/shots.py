"""Dev-only: prints CI screenshots into the job log as base64 JPEG chunks (decoded locally by decode_shots.py)."""
import base64
import io
import os
import sys

from PIL import Image

d = sys.argv[1] if len(sys.argv) > 1 else 'run/screenshots'
files = sorted((f for f in os.listdir(d) if f.endswith('.png')), key=lambda f: os.path.getmtime(os.path.join(d, f))) if os.path.isdir(d) else []
print('=== SHOTS', len(files))
for f in files:
    im = Image.open(os.path.join(d, f)).convert('RGB')
    im.thumbnail((960, 540), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=72, optimize=True)
    s = base64.b64encode(b.getvalue()).decode()
    print('=== SHOT', f[:-4], len(s))
    for i in range(0, len(s), 3000):
        print('B64:' + s[i:i + 3000])
    print('=== ENDSHOT')
