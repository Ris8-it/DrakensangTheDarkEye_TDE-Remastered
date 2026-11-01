"""Preview icons the way the player sees them: on light parchment (crop of a real tooltip screenshot) at 64 and 128 px,
next to native reference icons. Usage: python -I tools/preview_icons.py out.png icon1.dds|png [icon2 ...] [--ref native1.dds ...]"""
import sys, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(__file__)
SHOT = os.path.join(HERE, '..', 'docs', 'reviews', '2026-10-30', 'screenshots', 'Screenshot 2026-10-30 000011.png')
args = sys.argv[2:]; refs = []
if '--ref' in args: i = args.index('--ref'); refs = args[i + 1:]; args = args[:i]
paper = Image.open(SHOT).convert('RGB').crop((300, 470, 900, 760))   # empty parchment area
items = [(p, False) for p in refs] + [(p, True) for p in args]
cols = min(8, len(items)); rows = (len(items) + cols - 1) // cols
W, H = cols * 140, rows * 210
sheet = Image.new('RGB', (W, H))
for x in range(0, W, paper.width):
    for y in range(0, H, paper.height): sheet.paste(paper, (x, y))
d = ImageDraw.Draw(sheet)
for k, (p, ours) in enumerate(items):
    im = Image.open(p).convert('RGBA')
    x, y = (k % cols) * 140 + 6, (k // cols) * 210 + 4
    big = im.resize((128, 128), Image.LANCZOS); sheet.paste(big, (x, y), big)
    sm = im.resize((64, 64), Image.LANCZOS); sheet.paste(sm, (x + 32, y + 130), sm)
    d.text((x, y + 196), ('' if ours else 'REF ') + os.path.basename(p)[:20], fill=(60, 30, 10))
sheet.save(sys.argv[1]); print(sys.argv[1], len(items))
