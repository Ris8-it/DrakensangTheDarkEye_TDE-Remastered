"""Check and repair Drakensang saves against the INSTALLED pack. Game must be closed for 'fix'.

    python -I tools/maint/save_doctor.py check            newest save (or give .dsa paths after the command)
    python -I tools/maint/save_doctor.py check all        every save
    python -I tools/maint/save_doctor.py fix [paths]      backs the save up (<save>.before_doctor) then repairs
    python -I tools/maint/save_doctor.py find <text> [paths]   where a text (e.g. an item id) appears in a save

What 'check' looks for (each of these has crashed or broken a load before):
  - pack objects (Id arm_*) whose template no longer exists: "<Type> with Id '...' not found" on load
  - learned plans (_PartyReceipes) pointing at a recipe that was removed or renamed
  - bytes stored in TEXT columns (written by a careless tool; the game may not match them)
  - the same dialogue line listed twice in _Story_DialogTakeStatus
  - pragma integrity_check
'fix' converts stray bytes to text, remaps learned plans of merged items (RENAMED below) and drops other dead ones,
removes duplicate dialogue-status rows (keeping the highest status), and reports what is left for a human to decide.
"""
import os, sys, glob, shutil, sqlite3
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
STATIC = os.path.join(GAME, 'export', 'db', 'static.db4')
SAVES = os.path.join(os.path.expanduser('~'), 'Documents', 'Drakensang', 'profiles', 'default', 'save')
RENAMED = {  # removed recipe -> its replacement (the player keeps what they learned)
    'arm_rezept_tl_crab': 'arm_rezept_tl_ward1', 'arm_rezept_tl_toad': 'arm_rezept_tl_ward2', 'arm_rezept_tl_louse': 'arm_rezept_tl_ward3'}
SKIP = ('_Instance_Entry', '_Instance_MarkerPoint', '_Instance_SpawnPoint', '_Instance_Exit')
dec = lambda b: b.decode('cp1252', 'replace')

def templates():
    st = sqlite3.connect(f'file:{STATIC}?mode=ro', uri=True); st.text_factory = dec
    ids, recipes = set(), set()
    for (t,) in st.execute("select name from sqlite_master where type='table' and name like '_Template_%'").fetchall():
        try:
            rows = {r[0] for r in st.execute(f'select Id from "{t}"')}
        except sqlite3.OperationalError:
            continue
        ids |= rows
        if t == '_Template_Recipe': recipes = rows
    return ids, recipes

def saves(args):
    if args and args[0] == 'all': return sorted(glob.glob(os.path.join(SAVES, '*', '*.dsa')))
    if args: return args
    found = glob.glob(os.path.join(SAVES, '*', '*.dsa'))
    return [max(found, key=os.path.getmtime)] if found else []

def text_tables(S):
    for (t,) in S.execute("select name from sqlite_master where type='table' and (name like '_Instance_%' or name like '_Story_%')").fetchall():
        for _, c, ty, *_ in S.execute(f'pragma table_info("{t}")').fetchall():
            if (ty or '').upper() == 'TEXT': yield t, c

def check(path, ids, recipes, fix=False):
    if fix:
        bak = path + '.before_doctor'
        if not os.path.exists(bak): shutil.copy2(path, bak)
    S = sqlite3.connect(path); S.text_factory = dec
    rep = []
    blobs = sum(S.execute(f'select count(*) from "{t}" where typeof("{c}")=\'blob\'').fetchone()[0] for t, c in text_tables(S))
    if blobs:
        rep.append(f'{blobs} byte values in TEXT columns')
        if fix:
            for t, c in list(text_tables(S)): S.execute(f'update "{t}" set "{c}"=cast("{c}" as text) where typeof("{c}")=\'blob\'')
    have = [r[0] for r in S.execute('select Id from _PartyReceipes')]
    for rid in have:
        if rid in recipes: continue
        new = RENAMED.get(rid)
        rep.append(f'learned plan {rid} no longer exists' + (f' (-> {new})' if new else ''))
        if fix:
            if new and new in recipes and new not in have: S.execute('update _PartyReceipes set Id=? where Id=?', (new, rid)); have.append(new)
            else: S.execute('delete from _PartyReceipes where Id=?', (rid,))
    dup = S.execute('select count(*) from (select TakeId from _Story_DialogTakeStatus group by TakeId having count(*) > 1)').fetchone()[0]
    if dup:
        rep.append(f'{dup} dialogue lines listed twice')
        if fix:
            S.execute('delete from _Story_DialogTakeStatus where rowid not in (select rowid from _Story_DialogTakeStatus s where TakeStatus = '
                      '(select max(TakeStatus) from _Story_DialogTakeStatus x where x.TakeId = s.TakeId) group by TakeId)')
    for (t,) in S.execute("select name from sqlite_master where type='table' and name like '_Instance_%'").fetchall():
        if t in SKIP or 'Id' not in [r[1] for r in S.execute(f'pragma table_info("{t}")')]: continue
        for (i,) in S.execute(f"select distinct Id from \"{t}\" where Id like 'arm%'"):
            if i not in ids: rep.append(f'{t}: {i} has no template (needs a human: re-add the template or remove the object)')
    if fix: S.commit()
    if fix:
        S.close()   # rewrite with the bundled SQLite 3.6.1, the game's engine generation (see sync_save_world.py)
        import subprocess
        subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'sqlite3.exe'), path, 'vacuum;'], check=True)
        S = sqlite3.connect(path); S.text_factory = dec
    ok = S.execute('pragma integrity_check').fetchone()[0]
    if ok != 'ok': rep.append('INTEGRITY: ' + ok)
    name = os.path.relpath(path, SAVES) if path.startswith(SAVES) else path
    print(f'{name}: ' + ('clean' if not rep else ('fixed: ' if fix else 'PROBLEMS: ') + '; '.join(rep)))

def find(text, paths):
    needle = text.encode('cp1252')
    for path in paths:
        S = sqlite3.connect(path); S.text_factory = bytes
        for (t,) in S.execute("select name from sqlite_master where type='table'").fetchall():
            t = t.decode()
            for c in [r[1].decode() for r in S.execute(f'pragma table_info("{t}")')]:
                for rowid, v in S.execute(f'select rowid, "{c}" from "{t}" where instr(cast("{c}" as blob), ?) > 0', (needle,)):
                    v = v if isinstance(v, bytes) else str(v).encode()
                    i = v.find(needle); print(f'{os.path.basename(path)} {t}.{c} row {rowid}: ...{dec(v[max(0, i - 50):i + 70])}...')

if __name__ == '__main__':
    cmd, args = (sys.argv[1] if len(sys.argv) > 1 else 'check'), sys.argv[2:]
    if cmd == 'find':
        find(args[0], saves(args[1:]))
    else:
        ids, recipes = templates()
        for p in saves(args): check(p, ids, recipes, fix=(cmd == 'fix'))
