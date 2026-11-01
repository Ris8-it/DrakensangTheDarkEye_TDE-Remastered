"""Split a ChatGPT sheet of several icons into single source images (web workflow, 31 Oct).
python -I tools/art/split_sheet.py <sheet.png> <first number in WEB_ORDER.txt> [count] [merge e.g. 8+9,11+12]
merge: objects that are one item drawn in separate pieces (a pair of bracers), numbered left to right, top to bottom from 1 on this sheet.
Objects are found by their solid pixels (labels, speckle and the drawn glow are dropped), holes inside an object are kept,
and each object is saved as assets/armory_icons_v2/src/rm_<key>.png with a .reglow marker: batch_remastered.py post then adds
the native shadow + tier glow (dsa.make_icon) at icon size instead of keeping the sheet's glow."""
import sys, os, collections
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(__file__); A = os.path.join(HERE, '..', '..', 'assets', 'armory_icons_v2')
sheet, first = sys.argv[1], int(sys.argv[2])
count = int(sys.argv[3]) if len(sys.argv) > 3 else None
merges = [tuple(int(x) for x in g.split('+')) for g in sys.argv[4].split(',')] if len(sys.argv) > 4 else []
order = dict(l.split() for l in open(os.path.join(A, 'prompts', 'WEB_ORDER.txt')) if l.strip())
im = Image.open(sheet).convert('RGBA'); a = np.array(im)
r, g, b, al = (a[..., i].astype(int) for i in range(4))
solid = al >= 248          # objects are opaque; the drawn halo (any colour) is translucent

# connected components on a 1/4 grid; keep the big ones (objects), drop labels and specks
s = solid[::4, ::4]; H, W = s.shape; lab = np.zeros(s.shape, int); comps = []
for y in range(H):
    for x in range(W):
        if s[y, x] and not lab[y, x]:
            lab[y, x] = len(comps) + 1; q = collections.deque([(y, x)]); pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and s[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = lab[y, x]; q.append((ny, nx))
            ys, xs = zip(*pts); comps.append((len(pts), min(xs) * 4, min(ys) * 4, max(xs) * 4 + 4, max(ys) * 4 + 4))
big = [c for c in comps if c[0] > 0.06 * max(c[0] for c in comps)]   # thin weapons (crossbows, tridents) are small in pixel count
rows = sorted(big, key=lambda c: (c[2] + c[4]) / 2)
# group into rows by vertical centre, then left to right
grouped, cur = [], []
for c in rows:
    if cur and (c[2] + c[4]) / 2 - (cur[-1][2] + cur[-1][4]) / 2 > 0.5 * (cur[-1][4] - cur[-1][2]): grouped.append(cur); cur = []
    cur.append(c)
grouped.append(cur)
objs = [c for row in grouped for c in sorted(row, key=lambda c: c[1])]
multi = set()
for g in sorted(merges, key=lambda g: -g[0]):   # later groups first so earlier indexes stay valid
    parts = [objs[i - 1] for i in g]
    u = (sum(p[0] for p in parts), min(p[1] for p in parts), min(p[2] for p in parts), max(p[3] for p in parts), max(p[4] for p in parts))
    for i in sorted(g, reverse=True): del objs[i - 1]
    objs.insert(g[0] - 1, u); multi.add(u)
if count: objs = objs[:count]
print(len(objs), 'objects')
for n, (_, x0, y0, x1, y1) in enumerate(objs, first):
    key = order[str(n)]
    pad = 8; x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)
    crop = im.crop((x0, y0, x1, y1)); m = Image.fromarray((solid[y0:y1, x0:x1] * 255).astype('uint8'))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    # keep the LARGEST blob (the object); a thin bowstring or a speck near the centre must not win
    best, val = None, 0
    for v in range(1, 250):
        mm = np.array(m); ys, xs = np.nonzero(mm == 255)
        if not len(ys): break
        ImageDraw.floodfill(m, (int(xs[0]), int(ys[0])), v)
        size = int((np.array(m) == v).sum())
        if size > val: best, val = v, size
    if (_, x0 + pad if x0 else x0, y0, x1, y1) and any(u[1] - pad <= x0 + pad and u[3] + pad >= x1 - pad and u[2] - pad <= y0 + pad and u[4] + pad >= y1 - pad for u in multi):
        arr = np.array(m); sizes = {v: int((arr == v).sum()) for v in range(1, 250)}   # merged item: keep every big piece
        blob = Image.fromarray((np.isin(arr, [v for v, z in sizes.items() if z >= 0.25 * val]) * 255).astype('uint8'))
    else:
        blob = Image.fromarray(((np.array(m) == best) * 255).astype('uint8'))
    # fill holes: flood the outside from the border
    out = blob.copy(); ImageDraw.floodfill(out, (0, 0), 64)
    obj = Image.fromarray(((np.array(out) != 64) * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3))
    alpha = np.minimum(np.array(crop)[..., 3], np.array(obj.filter(ImageFilter.GaussianBlur(1))))
    rgba = np.array(crop); rgba[..., 3] = alpha
    piece = Image.fromarray(rgba); bb = piece.getbbox(); piece = piece.crop(bb)
    side = int(max(piece.size) * 1.06); sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(piece, ((side - piece.width) // 2, (side - piece.height) // 2))
    dst = os.path.join(A, 'src', f'{key}.png'); sq.save(dst); open(dst[:-4] + '.reglow', 'w').write('')
    print(n, key, sq.size)
