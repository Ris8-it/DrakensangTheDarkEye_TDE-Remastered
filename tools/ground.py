"""Ground under placed content, from the level's navigation graph (export/navigation/<level>.map in the player's own archives).

    python -I tools/ground.py check            every placed pack entity of the installed game.db4 vs the ground (report)
    python -I tools/ground.py at <level> x z   ground heights of the walk nodes near a point

The .map is an 8-connected walk grid (1 m or 0.5 m in x-z, y = ground height) plus irregular links (v2: i32 -1,-1,16,2,count;
node = f32 x y z, i32 n, i32 links[n], f32 size, i32 flag; then the connected components). Archives are searched newest first:
patch1.npk overrides export*.npk (location08, location10 and dungeon05_burg have patched maps). Inferred from the archive order.

Placement rule (used by quests.Story for monsters, NPCs and entry points), see judge(): a spot within vanilla's own spread of the
ground (vanilla monsters stand -0.3..+1.6 m above their walk node, 6 Nov) is kept; a wrong height over mapped ground is moved onto
the nearest fully linked node, 0.5 m up; an unmapped corner only warns; a spot with no node within 40 m fails the build.
"""
import math, os, sqlite3, struct, sys, collections
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
ARCHIVES = ('patch1', 'export_3', 'export_2', 'export_1', 'export')
KEEP_LOW, KEEP_HIGH = -0.3, 1.6   # metres above the walk node that count as standing on the ground (vanilla spread)
SNAP, LIFT, CELL, FAR = 3.0, 0.5, 4.0, 40.0
_toc, _maps = {}, {}


def _archive_toc():
    if not _toc:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import npk
        for a in ARCHIVES:
            p = os.path.join(GAME, a + '.npk')
            if not os.path.exists(p): continue
            off, files = npk.toc(p)
            for name, o, size in files:
                _toc.setdefault(name.lower(), (p, off, o, size))   # first archive wins (newest first)
    return _toc


def read_map(data):
    h = struct.unpack_from('<4i', data)
    if h[:3] == (-1, -1, 16): ver, n, o = h[3], struct.unpack_from('<i', data, 16)[0], 20
    else: ver, n, o = 0, h[0], 4
    nodes = []
    for _ in range(n):
        x, y, z, k = struct.unpack_from('<3fi', data, o); o += 16 + 4 * k
        o += 8 if ver == 2 else 4 if ver == 1 else 0
        nodes.append((x, y, z, k))
    return nodes


def nav(level, navmesh):
    """navmesh = _Instance_Levels.NavMesh ('export:navigation/<x>.map'). Returns a dict cell -> [(x, y, z, links)] or None."""
    if level not in _maps:
        key = ('export/' + navmesh.split(':', 1)[1]).lower() if navmesh and ':' in navmesh else ''
        hit = _archive_toc().get(key)
        if not hit: _maps[level] = None
        else:
            p, off, o, size = hit
            with open(p, 'rb') as f:
                f.seek(off + 8 + o); data = f.read(size)
            grid = collections.defaultdict(list)
            for node in read_map(data): grid[(int(node[0] // CELL), int(node[2] // CELL))].append(node)
            _maps[level] = grid
    return _maps[level]


def _near(grid, x, z, r):
    c = int(r // CELL) + 1
    for dx in range(-c, c + 1):
        for dz in range(-c, c + 1):
            for n in grid.get((int(x // CELL) + dx, int(z // CELL) + dz), ()):
                d = math.hypot(n[0] - x, n[2] - z)
                if d <= r: yield d, n


def judge(grid, x, y, z):
    """-> (state, (x, y, z) to use, note). state: 'ok' standing within vanilla's spread; 'fix' wrong height over mapped ground,
    moved onto the nearest fully linked node within SNAP; 'warn' no node within 2.5 m (vanilla NPCs stand in unmapped corners of
    halls and caves too, so this is not proof); 'fail' nothing within FAR m: off the map (a parked placeholder spot)."""
    best = min(((abs(y - n[1]) + d, d, n) for d, n in _near(grid, x, z, 2.5)), default=None, key=lambda t: t[0])
    if best is None:
        near = [(d, n) for d, n in _near(grid, x, z, SNAP) if n[3] >= 8] or list(_near(grid, x, z, SNAP))   # an edge node if nothing better
        if near:
            d, n = min(near, key=lambda t: t[0])
            return 'fix', (n[0], n[1] + LIFT, n[2]), f'next to the walk grid: moved {d:.1f} m to ground {n[1]:.2f} + {LIFT}'
        far = min((d for d, n in _near(grid, x, z, FAR)), default=None)
        if far is None: return 'fail', None, f'off the map: no walk node within {FAR:.0f} m'
        return 'warn', (x, y, z), f'unmapped spot: nearest walk node {far:.1f} m'
    dy = y - best[2][1]
    if KEEP_LOW <= dy <= KEEP_HIGH: return 'ok', (x, y, z), ''
    cands = [(abs(y - n[1]) * 0.5 + d, n) for d, n in _near(grid, x, z, SNAP) if n[3] >= 8] or [(0, best[2])]
    n = min(cands, key=lambda t: t[0])[1]
    return 'fix', (n[0], n[1] + LIFT, n[2]), f'{dy:+.1f} m from the ground: moved {math.hypot(n[0] - x, n[2] - z):.1f} m to ground {n[1]:.2f} + {LIFT}'


def check(game_db=None):
    g = sqlite3.connect(f"file:{game_db or os.path.join(GAME, 'export', 'db', 'game.db4')}?mode=ro", uri=True)
    g.text_factory = lambda b: b.decode('cp1252', 'replace')
    navs = dict(g.execute('select Id, NavMesh from _Instance_Levels'))
    bad = 0
    for t, col in (('Monster', 'Id'), ('NPC', 'Id'), ('Entry', 'Name')):
        for name, lvl, tr in g.execute(f'select {col}, _Level, Transform from _Instance_{t} where {col} like "arm_%"'):
            if lvl == '_graveyard_' or not tr: continue
            grid = nav(lvl, navs.get(lvl))
            if grid is None: print(f'  ?  {t} {name}: no navigation map for {lvl}'); continue
            x, y, z = struct.unpack('<16f', tr)[12:15]
            state, pos, note = judge(grid, x, y, z)
            if state != 'ok': print(f'  {state:4} {t:7} {name:42} {lvl:22} {note}')
            bad += state in ('fix', 'fail')
    print(f'{bad} placed pack entities off the ground or off the map (warn = unmapped spot, not counted)')
    return bad


if __name__ == '__main__':
    if sys.argv[1:2] == ['check']: sys.exit(1 if check(*sys.argv[2:3]) else 0)
    if sys.argv[1:2] == ['at']:
        lvl, x, z = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        g = sqlite3.connect(f"file:{os.path.join(GAME, 'export', 'db', 'game.db4')}?mode=ro", uri=True); g.text_factory = lambda b: b.decode('cp1252', 'replace')
        grid = nav(lvl, g.execute('select NavMesh from _Instance_Levels where Id=?', (lvl,)).fetchone()[0])
        for d, n in sorted(_near(grid, x, z, 3.0))[:12]: print(f'{d:4.1f} m  ground {n[1]:.2f}  links {n[3]}  ({n[0]:.1f}, {n[2]:.1f})')
