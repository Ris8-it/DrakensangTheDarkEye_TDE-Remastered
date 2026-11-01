"""Shrink icon source art to 512 px (lossless PNG, alpha kept). The game shows icons at 128 px; 512 leaves 4x headroom.
Codex and sheet splits write 1024-1600 px files: run this after new icons are processed.

    python -I tools/maint/slim_sources.py          (prints how much space it saved)
"""
import os, glob
from PIL import Image
SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'armory_icons_v2', 'src')
MAX = 512
before = after = n = 0
for p in glob.glob(os.path.join(SRC, '*.png')):
    size = os.path.getsize(p); before += size
    im = Image.open(p)
    if max(im.size) > MAX:
        im = im.convert('RGBA'); im.thumbnail((MAX, MAX), Image.LANCZOS)
        im.save(p, optimize=True); n += 1
    after += os.path.getsize(p)
print(f'{n} images shrunk; sources {before / 2**20:.0f} MB -> {after / 2**20:.0f} MB')
