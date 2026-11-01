"""Chest loot tables used by a single chest Id: value vs entry count (deterministic if value==0 or value>=count)."""
import sqlite3, sys, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec
use = collections.defaultdict(set)
for cid, lvl, lt, lock in g.execute("select Id,_Level,LootTable,LockPickingDifficulty from _Instance_Chest where LootTable<>''"): use[lt].add((cid, lvl, lock))
for lt, chests in sorted(use.items(), key=lambda x: sorted(x[1])[0][1]):
    r = s.execute("select LootTableValue, LootTableContent from _DSA_LootTables where LootTableName=?", (lt,)).fetchone()
    if not r: print('MISSING', lt); continue
    n = r[1].count(';'); ids = {c for c,_,_ in chests}
    if len(ids) == 1 and len(chests) == 1:
        det = r[0] == '0' or (r[0].isdigit() and int(r[0]) >= n)
        cid, lvl, lock = next(iter(chests))
        print(f"{lvl:30} {cid:48} lock={lock:<5} {lt:45} v={r[0]:>3} n={n} {'DET' if det else ''} | {r[1][:90]}")
