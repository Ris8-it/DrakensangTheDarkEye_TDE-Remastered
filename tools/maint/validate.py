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
EXTRA = ['unofficial_patch', 'world_systems', 'smarter_foes', 'engine_lab', 'engine_lab_stage2']   # optional modules (engine layers), tested after the pack
MODS = MODS + EXTRA
if '--mods' in sys.argv: MODS = sys.argv[sys.argv.index('--mods') + 1].split(',')     # e.g. --mods world_systems,engine_lab
if '--base' in sys.argv: BASE_SRC = sys.argv[sys.argv.index('--base') + 1]            # another clean baseline folder
DBS = ('static', 'locale', 'game')
fail = []

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlrun

def sql(db, script):
    return sqlrun.run_sql(db, script, SQ)

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
print(f'4c. placements on the ground ({_off} off)')

def script_problems(d):
    """Dangling script wiring (only problems NOT already in the baseline are reported): GUID refs in statements/conditions,
    script roots, state machines, presets, ScriptOverride/ScriptPreset/Behaviour/LevelEnterScript/CombatScriptName names."""
    import uuid as _u
    S = sqlite3.connect(os.path.join(d, 'static.db4')); S.text_factory = lambda b: b.decode('cp1252', 'replace')
    G = sqlite3.connect(os.path.join(d, 'game.db4')); G.text_factory = S.text_factory
    st = {r[0] for r in S.execute('select StatementGUID from _Scripts_Statements')}
    co = set()
    for tb in ('_Scripts_Conditions', '_Story_DialogConditions', '_Story_TaskOpenConditions', '_Story_TaskCloseConditions'):
        co |= {r[0] for r in S.execute(f'select ConditionGUID from {tb}')}
    blk = lambda s: _u.UUID(s).bytes_le
    out = set()
    for g, typ, c in S.execute('select StatementGUID, StatementType, StatementContent from _Scripts_Statements'):
        refs = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', c or '')
        if typ == 'Condition':
            if refs and blk(refs[0]) not in co: out.add(f'statement condition ref missing {refs[0]}')
        elif typ in ('Begin', 'Then', 'Else', 'If'):
            for r in refs:
                if blk(r) not in st: out.add(f'{typ} child missing {r}')
    for g, typ, c in S.execute('select ConditionGUID, ConditionType, ConditionContent from _Scripts_Conditions where ConditionType != \'Atom\''):
        for r in re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', c or ''):
            if blk(r) not in co: out.add(f'condition child missing {r}')
    acts = {r[0] for r in S.execute('select ScriptName from _Scripts_ActionScripts')}
    for n, ref in S.execute('select ScriptName, StatementRef from _Scripts_ActionScripts'):
        if ref not in st: out.add(f'action script {n}: root missing')
    conds = {r[0] for r in S.execute('select ScriptName from _Scripts_ConditionScripts')}
    machines = {r[0]: r[1] for r in S.execute('select Id, StartState from _Script_StateMachines')}
    states = {(r[0], r[1]) for r in S.execute('select MachineName, StateName from _Script_StateMachineStates')}
    for mid, start in machines.items():
        if (mid, start) not in states: out.add(f'machine {mid}: start state {start} missing')
    for mid, frm, to, cref in S.execute('select MachineName, StateName, ToState, ConditionRef from _Script_StateTransitions'):
        if (mid, to) not in states or (mid, frm) not in states: out.add(f'machine {mid}: transition {frm}->{to} to/from a missing state')
        if cref not in co: out.add(f'machine {mid}: transition {frm}->{to} condition missing')
    for col in ('OnEntry', 'OnFrame', 'OnExit'):
        for mid, sn, ref in S.execute(f'select MachineName, StateName, {col}StatementRef from _Script_StateMachineStates'):
            if ref and ref != bytes(16) and ref not in st: out.add(f'machine {mid}.{sn}: {col} block missing')
    presets = {r[0] for r in S.execute('select PresetName from _DSA_Preset')}
    for n, typ, sc in S.execute('select PresetName, PresetType, PresetScriptName from _DSA_Preset'):
        if sc not in (conds if typ == 'CanAction' else acts): out.add(f'preset {n}: {typ} script {sc} missing')
    for C, pre in ((S, '_Template_'), (G, '_Instance_')):
        for (tb,) in C.execute(f"select name from sqlite_master where type='table' and name like '{pre}%'"):
            cols = [x[1] for x in C.execute(f'pragma table_info("{tb}")')]
            if 'ScriptOverride' in cols:
                for (v,) in C.execute(f'select ScriptOverride from "{tb}" where ScriptOverride != \'\''):
                    for k, ev, sc in re.findall(r'(on|can):(\w+):([^;]+)', v):
                        if sc not in (acts if k == 'on' else conds): out.add(f'{tb}: {k}:{ev}:{sc} missing')
            if 'ScriptPreset' in cols:
                for (v,) in C.execute(f'select distinct ScriptPreset from "{tb}" where ScriptPreset != \'\''):
                    if v not in presets: out.add(f'{tb}: preset {v} missing')
            if 'Behaviour' in cols:
                for (v,) in C.execute(f'select distinct Behaviour from "{tb}" where Behaviour != \'\''):
                    if v not in machines: out.add(f'{tb}: behaviour {v} missing')
    for C, tb in ((G, '_Instance_Levels'), (S, '_Template_Levels')):
        for lvl, v in C.execute(f'select Id, LevelEnterScript from {tb} where LevelEnterScript != \'\''):
            for sc in v.split(','):
                if sc and sc not in acts: out.add(f'{tb} {lvl}: enter script {sc} missing')
    for aid, sc in S.execute("select Id, CombatScriptName from _Template_Attacks where CombatScriptName != ''"):
        if sc not in acts: out.add(f'attack {aid}: script {sc} missing')
    return out

new_probs = script_problems(TEST) - script_problems(BASE)
for p_ in sorted(new_probs): fail.append('script wiring: ' + p_)
print(f'4b. script wiring checked ({len(new_probs)} new problems)')

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
