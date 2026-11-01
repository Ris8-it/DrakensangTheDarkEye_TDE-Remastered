import sqlite3, sys
db = sys.argv[1]
dec = lambda b: b.decode('cp1252','replace')
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec
tables = [t for (t,) in g.execute("select name from sqlite_master where type='table'")]
for gid, name in g.execute("select Guid, Id from _Instance_NPC where Id like 'Cuano%'").fetchall():
    print(name, gid.hex())
    tot = 0
    for t in tables:
        if 'StorageGUID' not in [c[1] for c in g.execute(f'pragma table_info([{t}])')]: continue
        rows = g.execute(f"select Id, StackCount from [{t}] where StorageGUID=?", (gid,)).fetchall() if 'StackCount' in [c[1] for c in g.execute(f'pragma table_info([{t}])')] else g.execute(f"select Id, 1 from [{t}] where StorageGUID=?", (gid,)).fetchall()
        if rows: print('  ', t, rows); tot += len(rows)
    print('  total entries', tot)
