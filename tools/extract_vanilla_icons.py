"""Extract the game's own inventory icons from your installed copy (needed once before building; they are not in the repository).

    python -I tools/extract_vanilla_icons.py                       (game at D:/Steam/steamapps/common/Drakensang)
    set DRAKENSANG=C:/Games/Drakensang  then run it again          (any other install path)

Writes tools/research/out/icons_vanilla/*.dds (about 1100 files, 20 MB). Later archives win, like in the game: patch1 over export_*.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from npk import toc
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'research', 'out', 'icons_vanilla')
os.makedirs(OUT, exist_ok=True)
n = 0
for arc in ('export.npk', 'export_1.npk', 'export_2.npk', 'export_3.npk', 'patch1.npk'):
    path = os.path.join(GAME, arc)
    if not os.path.exists(path): continue
    dataoff, files = toc(path)
    with open(path, 'rb') as f:
        for name, off, size in files:
            low = name.lower().replace('\\', '/')
            if '/textures/icons/' not in '/' + low or not low.endswith('.dds'): continue
            f.seek(dataoff + 8 + off)
            with open(os.path.join(OUT, os.path.basename(name)), 'wb') as g: g.write(f.read(size))
            n += 1
print(f'{n} icons written to {OUT}' if n else f'No icons found: is the game at {GAME}? Set DRAKENSANG to its folder.')
