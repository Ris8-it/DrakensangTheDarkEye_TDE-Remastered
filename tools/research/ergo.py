import sqlite3, sys
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
def conn(n):
    c = sqlite3.connect(f'file:{db}/{n}?mode=ro', uri=True); c.text_factory = dec; c.row_factory = sqlite3.Row; return c
g, s, l = conn('game.db4'), conn('static.db4'), conn('locale.db4')
loc = {r[0]: r[1] for r in l.execute('select LocaId, LocaText from _Locale')}
owners = {}
for t in ('_Instance_NPC', '_Instance_Chest', '_Instance_PC'):
    for r in g.execute(f'select Guid, Id, LookAtText, _Level from {t}'): owners[r[0]] = (loc.get(r[2], r[1]), r[1], r[3])
tables = [t for (t,) in g.execute("select name from sqlite_master where type='table'")]
for t in tables:
    cols = [c[1] for c in g.execute(f'pragma table_info([{t}])')]
    if 'StorageGUID' not in cols: continue
    for r in g.execute(f"select * from [{t}] where hex(Guid) like '6572676F%'"):
        o = owners.get(r['StorageGUID'], ('?', '?', r['_Level']))
        stats = ''
        if 'WpW6' in cols: stats = f"{r['WpW6']}d6+{r['WpW6plus']} AT{r['WpATmod']:+} PA{r['WpPAmod']:+} INI{r['WpINI']:+}"
        print(f"{t[10:]:<8} {loc.get(r['LookAtText'], r['Id'])[:30]:<30} {stats:<22} eff={r['PermanentEffect'] if 'PermanentEffect' in cols else ''} | {loc.get(r['InfoIdentified'],'').replace(chr(92)+'n',' ')[-110:] if 'InfoIdentified' in cols else ''} | sold/held by: {o[0]} ({o[1]}, {o[2]})")
