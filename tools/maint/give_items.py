"""Give items to a party member in a save (game closed). Backs the save up as <save>.before_give, rewrites it with SQLite 3.6.1.

    python -I tools/maint/give_items.py <save.dsa> <pc id, e.g. CharWizardPC> <item id>[:count] [<item id>[:count] ...]

Each new object is a copy of an existing object of the same kind in the save, refreshed from the installed template (every
column the two tables share), with a new Guid, the party member as owner and the first free inventory slot.
"""
import os, sys, shutil, sqlite3, subprocess, uuid
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
STATIC = os.path.join(GAME, 'export', 'db', 'static.db4')
KINDS = ('Item', 'Weapon', 'Armor', 'Shield', 'Jewelry', 'Recipe', 'Ammo')
KEEP = {'Guid', '_ID', '_Level', '_Layers', 'Transform', 'StorageGUID', 'StorageSlotId', 'IsEquiped', 'EquipmentSlotId', 'StackCount'}

def main(save, pc, wanted):
    bak = save + '.before_give'
    if os.path.exists(bak):   # never keep only an old backup: the 6 Nov give had just the 2 Nov one to fall back on
        import time; bak += time.strftime('_%Y%m%d_%H%M%S')
    shutil.copy2(save, bak)
    S = sqlite3.connect(save); T = sqlite3.connect(f'file:{STATIC}?mode=ro', uri=True)
    S.text_factory = T.text_factory = bytes
    cols = lambda c, t: [r[1].decode() for r in c.execute(f'pragma table_info("{t}")')]
    owner = S.execute('select Guid, _Level from _Instance_PC where Id=? order by IsInPartySelection desc limit 1', (pc,)).fetchone()
    assert owner, f'no party member {pc}'
    g, lvl = owner
    used = set()
    for (t,) in S.execute("select name from sqlite_master where type='table' and name like '_Instance_%'").fetchall():
        c = cols(S, t.decode())
        if 'StorageGUID' in c and 'StorageSlotId' in c:
            used |= {r[0] for r in S.execute(f'select StorageSlotId from "{t.decode()}" where StorageGUID=?', (g,))}
    for w in wanted:
        iid, _, n = w.partition(':'); n = int(n or 1)
        kind = next((k for k in KINDS if T.execute(f'select 1 from "_Template_{k}" where Id=?', (iid,)).fetchone()), None)
        assert kind, f'{iid}: no template'
        ti, tt = f'_Instance_{kind}', f'_Template_{kind}'
        sc, tc = cols(S, ti), cols(T, tt)
        donor = S.execute(f'select * from "{ti}" where StorageGUID=? limit 1', (g,)).fetchone() or S.execute(f'select * from "{ti}" limit 1').fetchone()
        row = dict(zip(sc, donor))
        tmpl = dict(zip(tc, T.execute(f'select * from "{tt}" where Id=?', (iid,)).fetchone()))
        for c in sc:
            if c in tmpl and c not in KEEP: row[c] = tmpl[c]
        stack = int(tmpl.get('MaxStackCount') or 1) > 1
        for _ in range(1 if stack else n):
            slot = next(i for i in range(2000) if i not in used); used.add(slot)
            row.update(Guid=uuid.uuid4().bytes_le, StorageGUID=g, StorageSlotId=slot, _Level=lvl)
            if 'StackCount' in row: row['StackCount'] = n if stack else 1
            if 'IsEquiped' in row: row['IsEquiped'] = 0
            if 'EquipmentSlotId' in row: row['EquipmentSlotId'] = b''
            S.execute(f'insert into "{ti}" ({",".join(chr(34) + c + chr(34) for c in sc)}) values ({",".join("?" * len(sc))})', [row[c] for c in sc])
            S.execute('update _Instance_PC set StorageContentCount=coalesce(StorageContentCount,0)+1 where Guid=?', (g,))
        print(f'  + {iid} x{n} ({kind})')
    # text columns must stay text (bytes copied from the template are cast back)
    for (t,) in S.execute("select name from sqlite_master where type='table' and name like '_Instance_%'").fetchall():
        t = t.decode()
        for _, c, ty, *_ in S.execute(f'pragma table_info("{t}")').fetchall():
            if (ty or b'').upper() == b'TEXT': S.execute(f'update "{t}" set "{c.decode()}"=cast("{c.decode()}" as text) where typeof("{c.decode()}")=\'blob\'')
    S.commit(); S.close()
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'sqlite3.exe'), save, 'vacuum;'], check=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
