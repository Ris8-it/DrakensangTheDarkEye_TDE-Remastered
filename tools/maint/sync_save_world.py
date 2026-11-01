"""Bring an existing save in line with a new build of the pack (new placed monsters/NPCs, moved shop plans and items, new quest state).
Templates, texts and loot already come from the installed databases; this adds what a save keeps its own copy of. Game closed.

    python -I tools/maint/sync_save_world.py <save.dsa> <OLD installed game.db4> <NEW installed game.db4>

OLD = the game.db4 the save was played with (e.g. export/db/game.db4 before running Install.bat), NEW = a copy with the new build
installed (.work/test after a test install, or the live one after Install.bat). Only pack content (arm_*) is touched; items the
player already took are kept. Backs the save up as <save>.before_update. Afterwards run save_doctor.py check.
Edit SCOPE / the moved-NPC list below for each new change, and run it twice: the second run must change nothing.
"""
import sqlite3, sys, shutil, os
save, oldp, newp = sys.argv[1:4]
bak = save + '.before_update'
if not os.path.exists(bak): shutil.copy2(save, bak)
S = sqlite3.connect(save); O = sqlite3.connect(oldp); N = sqlite3.connect(newp)
for c in (S, O, N): c.text_factory = bytes
cols = lambda c, t: [r[1].decode() if isinstance(r[1], bytes) else r[1] for r in c.execute(f'pragma table_info("{t}")')]
OWNERS = ('_Instance_NPC', '_Instance_PC', '_Instance_Chest')
def bump(guid, d):
    for t in OWNERS:
        S.execute(f'update "{t}" set StorageContentCount=coalesce(StorageContentCount,0)+? where Guid=?', (d, guid))
log = []
SCOPE = {'_Instance_Monster': "Id like 'arm_mo_%'", '_Instance_NPC': "Id like 'arm_npc_%'", '_Instance_Recipe': "Id like 'arm_rezept_%'",
         '_Instance_Jewelry': "Id='arm_j_gambler'", '_Instance_Entry': "Name like 'arm_npc_cc_%_entry'",
         # shop stock the pack adds or moves (plan bases, moved items): every armour/weapon row that differs between the two builds
         '_Instance_Weapon': "Id <> 'ravenwing_saber'", '_Instance_Armor': "1"}   # the Ravenwing test copy is removed by armory_v2's installer
for t, where in SCOPE.items():
    sc, nc = cols(S, t), cols(N, t)
    common = [c for c in nc if c in sc]
    o = {r[0]: r for r in O.execute(f'select Guid, StorageGUID from "{t}" where {where}')} if 'StorageGUID' in nc else \
        {r[0]: (r[0], None) for r in O.execute(f'select Guid from "{t}" where {where}')}
    n = {r[0]: r for r in N.execute(f'select {",".join(chr(34) + c + chr(34) for c in common)} from "{t}" where {where}')}
    gi = common.index('Guid'); si = common.index('StorageGUID') if 'StorageGUID' in common else None
    have = {r[0] for r in S.execute(f'select Guid from "{t}"')}
    owned = ({r[0] for r in S.execute(f'select Id, {"StorageGUID" if si is not None else "NULL"}, Guid from "{t}" where Guid in ({",".join("?" * len(o))})', list(o))
              if r[1] != o[r[2]][1]} if o and si is not None else set())   # only items the player took out of their old spot
    for g, row in n.items():
        if g in o or g in have: continue
        if t in ('_Instance_Weapon', '_Instance_Jewelry') and row[common.index('Id')] in owned: continue   # moved item already looted
        S.execute(f'insert into "{t}" ({",".join(chr(34) + c + chr(34) for c in common)}) values ({",".join("?" * len(common))})', row)
        if si is not None and row[si]: bump(row[si], 1)
        log.append(('+', t, row[common.index('Id')].decode()))
    for g, orow in o.items():
        if g in n: continue
        cur = S.execute(f'select Id{", StorageGUID" if si is not None else ""} from "{t}" where Guid=?', (g,)).fetchone()
        if not cur: continue
        if si is not None and cur[1] != orow[1]: log.append(('kept (player has it)', t, cur[0].decode())); continue
        S.execute(f'delete from "{t}" where Guid=?', (g,))
        if si is not None and cur[1]: bump(cur[1], -1)
        log.append(('-', t, cur[0].decode()))
# the Crimson Circle waits in '_graveyard_' until Klingenhand's job (only if you have not taken it yet)
if not S.execute("select 1 from _Story_DialogTakeStatus where TakeId like 'arm_dlg_klingenhand%r_accept' and TakeStatus<>0").fetchone():
    for g, nid in N.execute("select Guid, Id from _Instance_NPC where Id like 'arm_npc_cc_%' and _Level='_graveyard_'"):
        r = S.execute("select _Level from _Instance_NPC where Guid=?", (g,)).fetchone()
        if r and r[0] != b'_graveyard_':
            S.execute("update _Instance_NPC set _Level='_graveyard_' where Guid=?", (g,))
            for t in ('_Instance_Weapon', '_Instance_Armor', '_Instance_Shield', '_Instance_Item', '_Instance_Jewelry', '_Instance_Money'):
                S.execute(f'update "{t}" set _Level=? where StorageGUID=?', ('_graveyard_', g))
            log.append(('parked', '_Instance_NPC', nid.decode()))
# pack NPCs that moved (Klingenhand: out of the Golden Lance, which only opens with Rhulana's quest)
for g, lvl, tr in N.execute("select Guid, _Level, Transform from _Instance_NPC where Id in ('arm_npc_klingenhand')"):
    if S.execute('update _Instance_NPC set _Level=?, Transform=? where Guid=? and _Level<>?', (lvl, tr, g, lvl)).rowcount:
        log.append(('moved', '_Instance_NPC', 'arm_npc_klingenhand -> ' + lvl.decode()))
# template-mirrored columns on every pack recipe and armour piece already in the world or in the party's bags (crafting rework, armour rules)
NS = sqlite3.connect(newp.replace('game.db4', 'static.db4')); NS.text_factory = bytes
for t, tt, cs in (('_Instance_Recipe', '_Template_Recipe', ('RecipeIngredients', 'RecipeResult', 'Difficulty')),
                  ('_Instance_Armor', '_Template_Armor', ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB', 'ArBE', 'ArMaterial', 'PermanentEffect'))):
    k = 0
    for (iid,) in S.execute(f'select distinct Id from "{t}" where Id like "arm_%"').fetchall():
        iid = iid.decode('cp1252')
        v = NS.execute(f'select {",".join(cs)} from "{tt}" where Id=?', (iid,)).fetchone()
        if v:
            v = [x.decode('cp1252') if isinstance(x, bytes) else x for x in v]   # TEXT columns: bind as text, never as blob
            k += S.execute(f'update "{t}" set {",".join(c + "=?" for c in cs)} where Id=? and ({" or ".join(c + " is not ?" for c in cs)})', (*v, iid, *v)).rowcount
    log.append(('~', t, f'{k} rows refreshed from templates'))
# monster stats are copied into each instance: living unique beasts and bosses get the new values (tools/beasts_data.py; the
# pack's own beasts). Dead ones stay dead. Use a NEW build that includes hard_ending if the player has it installed.
STATS = ('LEmax', 'LE', 'MR', 'AT', 'PA', 'RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB', 'Immunity', 'AuraStatuseffect')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from beasts_data import TOUGH
for t in ('_Instance_Monster', '_Instance_MonsterLarge', '_Instance_NPC'):
    sc = cols(S, t); cs = [c for c in STATS if c in sc and c in cols(N, t)]
    ids = [i for (ty, i) in TOUGH if '_Instance_' + ty == t] + ([r[0].decode() for r in N.execute(f"select distinct Id from \"{t}\" where Id like 'arm_mo_%'")] if t == '_Instance_Monster' else [])
    k = 0
    for iid in ids:
        v = N.execute(f'select {",".join(cs)} from "{t}" where Id=? limit 1', (iid,)).fetchone()
        if not v: continue
        v = [x.decode('cp1252') if isinstance(x, bytes) else x for x in v]
        alive = 'and coalesce(IsCurrentlyDead, 0) = 0' if 'IsCurrentlyDead' in sc else ''
        k += S.execute(f'update "{t}" set {",".join(c + "=?" for c in cs)} where Id=? {alive}', (*v, iid)).rowcount
    log.append(('~', t, f'{k} living unique monsters updated'))
# template-mirrored columns that changed on existing pack items
for t, iid, cs in (('_Instance_Recipe', 'arm_rezept_am_kosh_arrow', ('RecipeIngredients',)),
                   ('_Instance_Item', 'arm_x_dead_lockpick', ('CanDestroy', 'Gew', 'Name', 'LookAtText', 'InfoIdentified', 'InfoUnIdentified'))):
    v = N.execute(f'select {",".join(cs)} from "{t}" where Id=? limit 1', (iid,)).fetchone()
    if v:
        k = S.execute(f'update "{t}" set {",".join(c + "=?" for c in cs)} where Id=?', (*v, iid)).rowcount
        log.append(('~', t, f'{iid} x{k}'))
# quest state: the new dialog, its takes and the three journal tasks
for t, key, where in (('_Story_Dialogs', 'DialogId', "DialogId='arm_dlg_hagen'"), ('_Story_DialogTakeStatus', 'TakeId', "TakeId like 'arm_dlg_%'"),
                      ('_Story_Tasks', 'TaskId', "TaskId like 'arm_q_madpack%'")):
    c = cols(N, t)
    for row in N.execute(f'select {",".join(c)} from "{t}" where {where}'):
        row = [v.decode('cp1252') if isinstance(v, bytes) else v for v in row]   # story keys are TEXT: a bytes value would never match and would duplicate
        if not S.execute(f'select 1 from "{t}" where cast("{key}" as text)=?', (row[c.index(key)],)).fetchone():
            S.execute(f'insert into "{t}" ({",".join(c)}) values ({",".join("?" * len(c))})', row); log.append(('+', t, row[c.index(key)]))
# rows above were copied with bytes text: store every TEXT-declared value as text again (vanilla saves never hold blobs there)
for (t,) in S.execute("select name from sqlite_master where type='table' and (name like '_Instance_%' or name like '_Story_%')").fetchall():
    for _, c, ty, *_ in S.execute(f'pragma table_info("{t.decode()}")').fetchall():
        if ty.decode().upper() == 'TEXT':
            S.execute(f'update "{t.decode()}" set "{c.decode()}"=cast("{c.decode()}" as text) where typeof("{c.decode()}")=\'blob\'')
S.commit()
print(save)
for x in log: print('  ', *x)
print('  integrity:', S.execute('pragma integrity_check').fetchone()[0].decode())
