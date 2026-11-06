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
if os.path.exists(bak):   # always a fresh backup (an old one from days ago is no way back from today's sync)
    import time; bak += time.strftime('_%Y%m%d_%H%M%S')
shutil.copy2(save, bak)
S = sqlite3.connect(save); O = sqlite3.connect(oldp); N = sqlite3.connect(newp)
for c in (S, O, N): c.text_factory = bytes
cols = lambda c, t: [r[1].decode() if isinstance(r[1], bytes) else r[1] for r in c.execute(f'pragma table_info("{t}")')]
OWNERS = ('_Instance_NPC', '_Instance_PC', '_Instance_Chest')
def bump(guid, d):
    for t in OWNERS:
        S.execute(f'update "{t}" set StorageContentCount=coalesce(StorageContentCount,0)+? where Guid=?', (d, guid))
log = []
SCOPE = {'_Instance_Monster': "Id like 'arm_mo_%'", '_Instance_NPC': "Id like 'arm_npc_%'", '_Instance_Recipe': "Id like 'arm_rezept_%'",
         '_Instance_Jewelry': "Id='arm_j_gambler'", '_Instance_Entry': "Name like 'arm_npc_cc_%_entry' or Name like 'arm_npc_tg_%_entry'",
         '_Instance_Item': "Id like 'arm_q_tg_%' or (Id like 'arm_tr_%' and StorageGUID in (select Guid from _Instance_NPC))", '_Instance_Shield': "Id like 'arm_tg_%'",   # the guild's prizes and shop shields (2 Nov)
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
# duelists who moved (2 Nov: Faelwen out of the Moorbridge marshes, Wolfhart away from the Silver Falls; both close for good): a living
# duelist already standing at the old spot walks to the new one
for g, nid in N.execute("select Guid, Id from _Instance_NPC where Id like 'arm_npc_cc_%'").fetchall():   # duelists and their bodyguards
    e = N.execute("select _Level, Transform from _Instance_Entry where Name=?", (nid.decode() + '_entry',)).fetchone()
    d = S.execute("select cast(_Level as text), coalesce(IsCurrentlyDead, 0) from _Instance_NPC where Guid=?", (g,)).fetchone()
    lv = d[0].decode() if d and isinstance(d[0], bytes) else (d[0] if d else None)
    if not e or not d or lv == '_graveyard_' or d[1] or lv == e[0].decode(): continue
    S.execute("update _Instance_NPC set _Level=?, Transform=? where Guid=?", (e[0].decode(), e[1], g))
    for t in ('_Instance_Weapon', '_Instance_Armor', '_Instance_Shield', '_Instance_Item', '_Instance_Jewelry', '_Instance_Money'):
        S.execute(f'update "{t}" set _Level=? where StorageGUID=?', (e[0].decode(), g))
    log.append(('moved', '_Instance_NPC', f'{nid.decode()} {lv} -> {e[0].decode()}'))
# a moved NPC also keeps its old "home" (RoamingBasePosition, 3 floats) and walks back to it: Faelwen went looking for his Moorbridge
# spot on the Dark Forest slope (3 Nov). Anyone of ours standing in its entry's level with a home far from that entry gets both reset.
import struct as _st
for g, nid in N.execute("select Guid, Id from _Instance_NPC where Id like 'arm_npc_cc_%' or Id like 'arm_npc_tg_%'").fetchall():
    e = N.execute("select _Level, Transform from _Instance_Entry where Name=?", (nid.decode() + '_entry',)).fetchone()
    d = S.execute("select cast(_Level as text), coalesce(IsCurrentlyDead, 0), RoamingBasePosition from _Instance_NPC where Guid=?", (g,)).fetchone()
    if not e or not d or d[1]: continue
    lv = d[0].decode() if isinstance(d[0], bytes) else d[0]
    if lv != e[0].decode(): continue
    ep = _st.unpack('<16f', e[1])[12:15]
    home = _st.unpack('<3f', d[2]) if d[2] and len(d[2]) == 12 else None
    cur = _st.unpack('<16f', S.execute('select Transform from _Instance_NPC where Guid=?', (g,)).fetchone()[0])
    if cur[13] < ep[1] - 1.0:   # sunk into the ground below its spot (an Elf-Tracker soft-locked a fight, 3 Nov): lift it back up
        m2 = list(cur); m2[13] = ep[1] + 1.0
        S.execute('update _Instance_NPC set Transform=? where Guid=?', (_st.pack('<16f', *m2), g)); log.append(('lifted', '_Instance_NPC', nid.decode()))
    if home and sum((a - b) ** 2 for a, b in zip(home, ep)) ** 0.5 <= 10: continue
    S.execute("update _Instance_NPC set Transform=?, RoamingBasePosition=?, RoamingBasePositionSet=1 where Guid=?", (e[1], _st.pack('<3f', *ep), g))
    log.append(('home reset', '_Instance_NPC', nid.decode()))
# the duelists' bodyguards (2 Nov): if the job was already taken, each living duelist's guards walk to their spot now
if S.execute("select 1 from _Story_DialogTakeStatus where TakeId like 'arm_dlg_klingenhand%r_accept' and TakeStatus<>0").fetchone():
    for g, gid in N.execute("select Guid, Id from _Instance_NPC where Id like 'arm_npc_cc_%_g_' and _Level='_graveyard_'").fetchall():
        gid = gid.decode(); duel = gid.rsplit('_g', 1)[0]
        d = S.execute("select _Level, coalesce(IsCurrentlyDead, 0) from _Instance_NPC where Id=?", (duel,)).fetchone()
        e = N.execute("select _Level, Transform from _Instance_Entry where Name=?", (gid + '_entry',)).fetchone()
        if not d or d[0] == b'_graveyard_' or d[1] or not e: continue
        if S.execute("update _Instance_NPC set _Level=?, Transform=? where Guid=? and cast(_Level as text)='_graveyard_'", (e[0].decode(), e[1], g)).rowcount:
            for t in ('_Instance_Weapon', '_Instance_Armor', '_Instance_Shield', '_Instance_Item', '_Instance_Jewelry', '_Instance_Money'):
                S.execute(f'update "{t}" set _Level=? where StorageGUID=?', (e[0].decode(), g))
            log.append(('arrived', '_Instance_NPC', gid))
# pack NPCs that moved (Klingenhand: out of the Golden Lance, which only opens with Rhulana's quest)
for g, lvl, tr in N.execute("select Guid, _Level, Transform from _Instance_NPC where Id in ('arm_npc_klingenhand')"):
    lvl = lvl.decode('cp1252')   # TEXT: bind as text (a bytes value never compares equal and would be stored as a blob)
    if S.execute('update _Instance_NPC set _Level=?, Transform=? where Guid=? and (_Level is not ? or Transform is not ?)', (lvl, tr, g, lvl, tr)).rowcount:
        log.append(('moved', '_Instance_NPC', 'arm_npc_klingenhand -> ' + lvl))
# three-way merge for characters: a column the new build changed (OLD -> NEW) is copied into the save only where the save still
# holds the OLD value, so play (levels, learned spells, positions) always wins. Covers vanilla edits like a trainer's teaching list,
# a companion's spell, a turned NPC.
for t in ('_Instance_NPC', '_Instance_PC'):
    cs = [c for c in cols(N, t) if c in cols(O, t) and c in cols(S, t) and c not in ('Guid', '_ID')]
    q = f'select Guid, {",".join(chr(34) + c + chr(34) for c in cs)} from "{t}"'
    old = {r[0]: r[1:] for r in O.execute(q)}
    text_cols = {r[1].decode() for r in S.execute(f'pragma table_info("{t}")') if (r[2] or b'').upper() == b'TEXT'}
    k = 0
    for r in N.execute(q):
        o = old.get(r[0])
        if not o: continue
        for c, ov, nv in zip(cs, o, r[1:]):
            if ov == nv: continue
            if c in text_cols:   # TEXT values must be bound as text, or they never compare equal (and must never be stored as blobs)
                ov, nv = (x.decode('cp1252') if isinstance(x, bytes) else x for x in (ov, nv))
            if S.execute(f'update "{t}" set "{c}"=? where Guid=? and "{c}" is ?', (nv, r[0], ov)).rowcount: k += 1
    log.append(('~', t, f'{k} values merged from the new build'))
# template-mirrored columns on every pack recipe and armour piece already in the world or in the party's bags (crafting rework, armour rules)
NS = sqlite3.connect(newp.replace('game.db4', 'static.db4')); NS.text_factory = bytes
for t, tt, cs in (('_Instance_Recipe', '_Template_Recipe', ('RecipeIngredients', 'RecipeResult', 'Difficulty')),
                  ('_Instance_Armor', '_Template_Armor', ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB', 'ArBE', 'ArMaterial', 'PermanentEffect')),
                  ('_Instance_Weapon', '_Template_Weapon', ('Graphics', 'WpW6', 'WpW6plus', 'WpATmod', 'WpPAmod', 'WpINI', 'MaxStackCount', 'ScriptOverride',
                                                            'PermanentEffect', 'IconBrush', 'TaAttr'))):
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
STATS = ('LEmax', 'LE', 'MR', 'AT', 'PA', 'AW', 'ATW6', 'ATW6plus', 'RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB', 'Immunity',
         'AuraStatuseffect', 'SpecialAttackChances', 'Behaviour', 'IsVictoryWorthy', 'AEmax', 'AE', 'ZaKulminatio', 'ZaCorpofrigo', 'ZaPlumbumbarum', 'ZaIgnifaxius',
         'ZaFulminictus', 'ZaParalysis', 'ZaSomnigravis')
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
for t, key, where in (('_Story_Dialogs', 'DialogId', "DialogId like 'arm_dlg_%'"),
                      ('_Story_DialogTakeStatus', 'TakeId', "TakeId like 'arm_dlg_%' or TakeId like 'Cuanoarm_tg_%' or TakeId like 'loc02_rakoriumarm_%' or TakeId like 'Loc03AllwissDialogarm_%'"),
                      ('_Story_Tasks', 'TaskId', "TaskId like 'arm_q_%'")):
    c = cols(N, t)
    for row in N.execute(f'select {",".join(c)} from "{t}" where {where}'):
        row = [v.decode('cp1252') if isinstance(v, bytes) else v for v in row]   # story keys are TEXT: a bytes value would never match and would duplicate
        if not S.execute(f'select 1 from "{t}" where cast("{key}" as text)=?', (row[c.index(key)],)).fetchone():
            S.execute(f'insert into "{t}" ({",".join(c)}) values ({",".join("?" * len(c))})', row); log.append(('+', t, row[c.index(key)]))
# ground (6 Nov, tools/ground.py): a living pack being whose spot IN THE SAVE floats, is buried or is off the map goes to its spot in
# the new build (which the build already put on the ground) and gets that spot as its home, or it walks back. Spots that play
# moved onto good ground are kept. Only where the new build has the being in the same level.
import ground
_navs = {r[0].decode(): r[1].decode() if r[1] else '' for r in N.execute('select Id, NavMesh from _Instance_Levels')}
for t in ('_Instance_Monster', '_Instance_NPC'):
    sc = cols(S, t)
    for g, iid, lvl, tr in N.execute(f"select Guid, Id, _Level, Transform from \"{t}\" where Id like 'arm_%' and _Level <> '_graveyard_'").fetchall():
        d = S.execute(f'select cast(_Level as text), coalesce(IsCurrentlyDead, 0), Transform from "{t}" where Guid=?', (g,)).fetchone()
        if not d or d[1] or (d[0].decode() if isinstance(d[0], bytes) else d[0]) != lvl.decode() or not d[2]: continue
        grid = ground.nav(lvl.decode(), _navs.get(lvl.decode()))
        if grid is None: continue
        state, _, note = ground.judge(grid, *_st.unpack('<16f', d[2])[12:15])
        if state not in ('fix', 'fail') or d[2] == tr: continue
        np_ = _st.unpack('<16f', tr)[12:15]
        S.execute(f'update "{t}" set Transform=?' + (', RoamingBasePosition=?, RoamingBasePositionSet=1' if 'RoamingBasePosition' in sc else '') + ' where Guid=?',
                  (tr, _st.pack('<3f', *np_), g) if 'RoamingBasePosition' in sc else (tr, g))
        log.append(('grounded', t, f'{iid.decode()}: {note.split(":")[0]}'))
# rows above were copied with bytes text: store every TEXT-declared value as text again (vanilla saves never hold blobs there)
for (t,) in S.execute("select name from sqlite_master where type='table' and (name like '_Instance_%' or name like '_Story_%')").fetchall():
    for _, c, ty, *_ in S.execute(f'pragma table_info("{t.decode()}")').fetchall():
        if ty.decode().upper() == 'TEXT':
            S.execute(f'update "{t.decode()}" set "{c.decode()}"=cast("{c.decode()}" as text) where typeof("{c.decode()}")=\'blob\'')
S.commit()
S.close()
# finish with the game's own engine generation: the bundled SQLite 3.6.1 rewrites the whole file (Python's modern SQLite
# leaves a newer layout behind; the 2008 game then failed to load story tables now and then, 2 Nov)
import subprocess
subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'sqlite3.exe'), save, 'vacuum;'], check=True)
S = sqlite3.connect(save); S.text_factory = bytes
print(save)
for x in log: print('  ', *x)
print('  integrity:', S.execute('pragma integrity_check').fetchone()[0].decode())
