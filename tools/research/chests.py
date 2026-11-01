"""List chests per level: lock difficulty, loot table, explicit contents with total value."""
import sqlite3, sys, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec
tabs = [t for (t,) in g.execute("select name from sqlite_master where type='table' and name like '_Instance_%'") if {'StorageGUID','Value'} <= {c[1] for c in g.execute(f'pragma table_info({t})')}]
cont = collections.defaultdict(list)
for t in tabs:
    for sg, i, v in g.execute(f'select StorageGUID, Id, Value from {t} where StorageGUID is not null'): cont[sg].append((i, v or 0))
lv = None
for guid, lvl, cid, locked, lpd, lt, ss, n in g.execute("select Guid,_Level,Id,IsLocked,LockPickingDifficulty,LootTable,SetupStorage,StorageContentCount from _Instance_Chest order by _Level, Id"):
    if lvl != lv: print('##', lvl); lv = lvl
    items = cont.get(guid, [])
    print(f"  {cid:40} lock={locked}/{lpd} lt={lt!s:18} ss={ss!s:14} n={n} val={sum(v for _,v in items)} top={sorted(items,key=lambda x:-x[1])[:2]}")
