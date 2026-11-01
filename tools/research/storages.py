"""Owners with explicit contents: chests (no loot table), hostile NPCs/monsters with items, merchants."""
import sqlite3, sys, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec
tabs = [t for (t,) in g.execute("select name from sqlite_master where type='table' and name like '_Instance_%'") if {'StorageGUID','Value'} <= {c[1] for c in g.execute(f'pragma table_info({t})')}]
cont = collections.defaultdict(list)
for t in tabs:
    for sg, i, v, sc in g.execute(f"select StorageGUID, Id, Value, {'StackCount' if 'StackCount' in [c[1] for c in g.execute(f'pragma table_info({t})')] else '1'} from {t} where StorageGUID is not null"): cont[sg].append((i, v or 0, sc))
print('### CHESTS with explicit contents and no loot table')
for guid, lvl, cid, lpd, n in g.execute("select Guid,_Level,Id,LockPickingDifficulty,StorageContentCount from _Instance_Chest where (LootTable is null or LootTable='') and StorageContentCount>0 order by _Level"):
    it = cont.get(guid, []); print(f"  {lvl:28} {cid:45} lock={lpd} n={n}/{len(it)} {[i for i,_,_ in it][:5]}")
print('### NPCs (non-friendly or merchants) with explicit contents')
for guid, lvl, nid, fac, rf, n in g.execute("select Guid,_Level,Id,Faction,RetailFactor,StorageContentCount from _Instance_NPC where StorageContentCount>0 order by _Level"):
    it = cont.get(guid, [])
    merchant = any(sc == -1 for _,_,sc in it)
    if fac != 'FaAllFriendly' or merchant:
        print(f"  {lvl:28} {nid:40} {fac:14} {'MERCHANT' if merchant else '':8} n={n}/{len(it)} {sorted(set(i for i,_,_ in it))[:4]}")
mc = {c[1] for c in g.execute('pragma table_info(_Instance_Monster)')}
print('### MONSTERS with explicit contents')
for guid, lvl, mid, n in g.execute("select Guid,_Level,Id,StorageContentCount from _Instance_Monster where StorageContentCount>0 order by _Level"):
    print(f"  {lvl:28} {mid:40} n={n} {[i for i,_,_ in cont.get(guid, [])][:4]}")
