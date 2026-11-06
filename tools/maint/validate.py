"""Full offline test of the whole pack on copies of the clean databases. Never touches the game's live files.

    python -I tools/maint/validate.py            (add --spoilers to also list journal/dialogue lines naming later places)

What it does, in order:
 1. copies the clean baseline (<game>/export/db/armory_backup) to .work/base and .work/test
 2. installs every module twice on .work/test (proves the installs are idempotent)
 3. runs each module's verify_*.sql: every "(expect N): M" must have N == M, every "owners whose count differs" must be 0
 4. checks references on the installed copy: loot tables, recipe ingredients/results, dialog and task actions all point at
    templates that exist; every IsDead target is a placed monster
 5. uninstalls everything twice and compares every table with the baseline (must be identical)
Exit code 0 = all good. Results are printed; nothing is written outside .work/.
"""
import os, sys, re, shutil, sqlite3, subprocess, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
BASE_SRC = os.path.join(GAME, 'export', 'db', 'armory_backup')
WORK = os.path.join(ROOT, '.work'); BASE = os.path.join(WORK, 'base'); TEST = os.path.join(WORK, 'test')
SQ = os.path.join(ROOT, 'tools', 'bin', 'sqlite3.exe')
MODS = ['armory_v2', 'arcane_thief', 'remastered_systems', 'quest_avestrue', 'secret_quests', 'hard_ending']   # install order
DBS = ('static', 'locale', 'game')
fail = []

def sql(db, script):
    with open(script, 'rb') as f:
        r = subprocess.run([SQ, db], stdin=f, capture_output=True)
    return r.stdout.decode('cp1252', 'replace') + r.stderr.decode('cp1252', 'replace')

def run(prefix):
    for mod in (MODS if prefix == '' else reversed(MODS)):
        for d in DBS:
            p = os.path.join(ROOT, 'mods', mod, 'sql', f'{prefix}{d}.sql')
            if os.path.exists(p):
                out = sql(os.path.join(TEST, f'{d}.db4'), p)
                for line in out.splitlines():
                    if 'error' in line.lower(): fail.append(f'{mod} {prefix}{d}: {line}')

def tables(db):
    c = sqlite3.connect(db); c.text_factory = bytes
    names = [r[0].decode() for r in c.execute("select name from sqlite_master where type='table'")]
    return {n: hashlib.md5(b''.join(repr(r).encode() for r in c.execute(f'select * from "{n}" order by 1'))).hexdigest() for n in names}

os.makedirs(WORK, exist_ok=True)
for d in (BASE, TEST):
    os.makedirs(d, exist_ok=True)
    for n in DBS: shutil.copy2(os.path.join(BASE_SRC, f'{n}.db4'), d)
print('1. baseline copied from', BASE_SRC)

run(''); run('')
print('2. installed twice')

for mod in MODS:
    for d in DBS:
        p = os.path.join(ROOT, 'mods', mod, 'sql', f'verify_{d}.sql')
        if not os.path.exists(p): continue
        out = sql(os.path.join(TEST, f'{d}.db4'), p)
        for a, b in re.findall(r'\(expect (\d+)\): (\d+)', out):
            if a != b: fail.append(f'{mod} verify_{d}: expected {a}, got {b}')
        for n in re.findall(r'differs from their items: (\d+)', out):
            if n != '0': fail.append(f'{mod} verify_{d}: {n} owners with wrong item counts')
        if 'integrity check' in out and '\nok' not in out: fail.append(f'{mod} {d}: integrity check failed')
print('3. verify scripts done')

s = sqlite3.connect(os.path.join(TEST, 'static.db4')); s.text_factory = lambda b: b.decode('cp1252', 'replace')
g = sqlite3.connect(os.path.join(TEST, 'game.db4')); g.text_factory = s.text_factory
ids = set()
for (t,) in s.execute("select name from sqlite_master where type='table' and name like '_Template_%'").fetchall():
    try: ids |= {r[0] for r in s.execute(f'select Id from "{t}"')}
    except sqlite3.OperationalError: pass
refs = 0
for n, c in s.execute('select LootTableName, LootTableContent from _DSA_LootTables'):
    for e in (c or '').split(';'):
        p = e.split('/')
        if len(p) > 2 and p[0] != 'Money' and p[1] not in ids: fail.append(f'loot table {n}: unknown {p[1]}'); refs += 1
for i, ing, res in s.execute("select Id, RecipeIngredients, RecipeResult from _Template_Recipe where Id like 'arm_%'"):
    for e in (ing or '').split(';') + [res or '']:
        p = e.split('/')
        if len(p) > 2 and p[1] not in ids: fail.append(f'recipe {i}: unknown {p[1]}'); refs += 1
for (a,) in s.execute('select ActionContent from _Story_DialogActions union all select ActionContent from _Story_TaskCloseActions union all select ActionContent from _Story_TaskOpenActions'):
    for m in re.finditer(r'templateId="([^"]+)"', a or ''):
        if m.group(1) not in ids: fail.append(f'action: unknown {m.group(1)}'); refs += 1
placed = {r[0] for r in g.execute("select Id from _Instance_Monster where Id like 'arm_mo_%'")} | {r[0] for r in g.execute("select Id from _Instance_NPC where Id like 'arm_%'")}
for (c,) in s.execute('select ConditionContent from _Story_TaskCloseConditions union all select ConditionContent from _Story_DialogConditions'):
    for m in re.finditer(r'IsDead who="(arm_[^"]+)"', c or ''):
        if m.group(1) not in placed: fail.append(f'IsDead target not placed: {m.group(1)}'); refs += 1
print(f'4. references checked ({refs} broken)')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ground   # every placed pack monster/NPC/entry on the ground of its level (6 Nov: Grimtusk stood off the map)
_off = ground.check(os.path.join(TEST, 'game.db4'))
if _off: fail.append(f'{_off} placed pack entities off the ground or off the map')
print(f'4b. placements on the ground ({_off} off)')

if '--spoilers' in sys.argv:
    subprocess.run([sys.executable, '-I', os.path.join(os.path.dirname(__file__), 'spoiler_scan.py'), TEST, BASE])

run('undo_'); run('undo_')
diff = 0
for d in DBS:
    a, b = tables(os.path.join(BASE, f'{d}.db4')), tables(os.path.join(TEST, f'{d}.db4'))
    for n in set(a) | set(b):
        if a.get(n) != b.get(n): fail.append(f'after uninstall {d}.{n} differs from the baseline'); diff += 1
print(f'5. uninstalled twice ({diff} tables differ from the baseline)')

print('\nRESULT:', 'ALL GOOD' if not fail else f'{len(fail)} PROBLEMS')
for f in fail[:60]: print('  -', f)
sys.exit(1 if fail else 0)
