"""Is everything a plan consumes actually obtainable? (A plan whose base item exists nowhere can never be crafted.)

    python -I tools/maint/obtainable.py        installs the pack on .work/test, then lists every consumed item with no source

A source is: a placed instance (shop stock, chest, carried gear) in game.db, a loot / skinning / pickpocket table entry, a monster's or
NPC's SetupStorage, a dialog or task action that creates it, or another plan that makes it. Debug chests don't count.
"""
import os, sys, re, shutil, sqlite3, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
BASE = os.path.join(GAME, 'export', 'db', 'armory_backup'); TEST = os.path.join(ROOT, '.work', 'test')
SQ = os.path.join(ROOT, 'tools', 'bin', 'sqlite3.exe')
MODS = ['armory_v2', 'arcane_thief', 'remastered_systems', 'quest_avestrue', 'secret_quests']
os.makedirs(TEST, exist_ok=True)
for d in ('static', 'locale', 'game'): shutil.copy2(os.path.join(BASE, f'{d}.db4'), TEST)
for mod in MODS:
    for d in ('static', 'locale', 'game'):
        p = os.path.join(ROOT, 'mods', mod, 'sql', f'{d}.sql')
        if os.path.exists(p):
            with open(p, 'rb') as f: subprocess.run([SQ, os.path.join(TEST, f'{d}.db4')], stdin=f, capture_output=True)
dec = lambda b: b.decode('cp1252', 'replace')
s = sqlite3.connect(os.path.join(TEST, 'static.db4')); s.text_factory = dec
g = sqlite3.connect(os.path.join(TEST, 'game.db4')); g.text_factory = dec
src = set()
for (t,) in g.execute("select name from sqlite_master where type='table' and name like '_Instance_%'").fetchall():
    cols = [r[1] for r in g.execute(f'pragma table_info("{t}")')]
    if 'Id' in cols and 'StorageGUID' in cols and t != '_Instance_Chest':
        src |= {r[0] for r in g.execute(f"""select distinct i.Id from "{t}" i where not exists
                 (select 1 from _Instance_Chest c where c.Guid = i.StorageGUID and c.Id like 'debug%')""")}
for (c,) in s.execute('select LootTableContent from _DSA_LootTables'):
    src |= {e.split('/')[1] for e in (c or '').split(';') if e.count('/') >= 2}
for t in ('_Template_Monster', '_Template_NPC', '_Template_MonsterLarge'):
    try:
        for (c,) in s.execute(f"select SetupStorage from \"{t}\" where SetupStorage<>''"):
            src |= {re.split('[/:]', e)[1] for e in c.split(';') if '/' in e}
    except sqlite3.OperationalError: pass
for (a,) in s.execute('select ActionContent from _Story_DialogActions union all select ActionContent from _Story_TaskCloseActions union all select ActionContent from _Story_TaskOpenActions'):
    src |= set(re.findall(r'templateId="([^"]+)"', a or ''))
made = {}
for rid, ing, res in s.execute('select Id, RecipeIngredients, RecipeResult from _Template_Recipe'):
    if res and res.count('/') >= 1: made[res.split('/')[1]] = rid
src |= set(made)
missing = {}
for rid, ing in s.execute("select Id, RecipeIngredients from _Template_Recipe where Id like 'arm_%'"):
    for e in (ing or '').split(';'):
        p = e.split('/')
        if len(p) >= 2 and p[1] not in src: missing.setdefault(p[1], []).append(rid)
for iid, rids in sorted(missing.items()):
    print(f'{iid:40} no source; needed by {", ".join(rids)}')
print('consumed items with no source:', len(missing))

# ---- timing: a plan sold before its base item can be had (e.g. a Ferdok plan whose base is only sold after Grimmzahn) ----
def stage(level, owner=''):
    n = re.search(r'(?:location|dungeon|loc|dun)_?(\d\d)', level or '')
    st = 0 if not n else 0 if int(n.group(1)) <= 2 else 1 if int(n.group(1)) <= 5 else 2 if int(n.group(1)) <= 8 else 3
    return max(st, 1) if re.search(r'nach_?loc05', owner or '') else st   # merchants' "after Grimmzahn" stock
earliest = {}
def seen(iid, st):
    earliest[iid] = min(st, earliest.get(iid, 9))
for (t,) in g.execute("select name from sqlite_master where type='table' and name like '_Instance_%'").fetchall():
    cols = [r[1] for r in g.execute(f'pragma table_info("{t}")')]
    if 'Id' in cols and 'StorageGUID' in cols and t != '_Instance_Chest':
        for iid, lvl, owner in g.execute(f"""select i.Id, i._Level, coalesce(n.Id, c.Id, '') from "{t}" i left join _Instance_NPC n on n.Guid = i.StorageGUID
                                            left join _Instance_Chest c on c.Guid = i.StorageGUID where coalesce(c.Id, '') not like 'debug%'"""):
            seen(iid, stage(lvl, owner))
for name, c in s.execute('select LootTableName, LootTableContent from _DSA_LootTables'):
    for e in (c or '').split(';'):
        if e.count('/') >= 2: seen(e.split('/')[1], stage(name))
late = []
for rid, ing in s.execute("select Id, RecipeIngredients from _Template_Recipe where Id like 'arm_%'"):
    sold = [stage(l, o) for l, o in g.execute('select i._Level, n.Id from _Instance_Recipe i join _Instance_NPC n on n.Guid = i.StorageGUID where i.Id=?', (rid,))]
    if not sold: continue
    for e in (ing or '').split(';'):
        p = e.split('/')
        if len(p) >= 2 and p[1] in earliest and p[1] not in made and earliest[p[1]] > min(sold):
            late.append((rid, p[1], min(sold), earliest[p[1]]))
STAGES = ('early', 'mid', 'late', 'endgame')
for rid, iid, a, b in late:
    print(f'{rid:36} sold {STAGES[a]}, but {iid} first available {STAGES[b]}')
print('plans sold before their base:', len(late), '(trophies come from skinning and are not counted here)')
