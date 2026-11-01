"""Test helper: also put one Ravenwing Saber in Rhulana's starting backpack."""
import sqlite3, sys, os, uuid
db, out = sys.argv[1], sys.argv[2]
dec = lambda b: b.decode('cp1252', 'replace')
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
src = dict(g.execute("select * from _Instance_Weapon where Id='ravenwing_saber' and StorageGUID=(select Guid from _Instance_NPC where Id='Cuano')").fetchone())
rh = g.execute("select Guid, _Level from _Instance_PC where Id='pc_rhulana'").fetchone()
src['Guid'] = uuid.uuid5(uuid.NAMESPACE_URL, 'drakensang/ravenwing_saber/pc_rhulana').bytes
src['StorageGUID'], src['_Level'] = rh['Guid'], rh['_Level']
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, bytes): return "X'" + v.hex().upper() + "'"
    if isinstance(v, (int, float)): return repr(v)
    return "'" + str(v).replace("'", "''") + "'"
G = lit(src['Guid'])
add = [f"UPDATE _Instance_PC SET StorageContentCount=StorageContentCount+1 WHERE Id='pc_rhulana' AND NOT EXISTS (SELECT 1 FROM _Instance_Weapon WHERE Guid={G});",
       f"INSERT OR IGNORE INTO _Instance_Weapon ({','.join(src)}) VALUES ({','.join(lit(v) for v in src.values())});"]
undo = [f"UPDATE _Instance_PC SET StorageContentCount=StorageContentCount-1 WHERE Id='pc_rhulana' AND EXISTS (SELECT 1 FROM _Instance_Weapon WHERE Guid={G});",
        f"DELETE FROM _Instance_Weapon WHERE Guid={G};"]
for name, lines in (('test_rhulana.sql', add), ('undo_test_rhulana.sql', undo)):
    with open(os.path.join(out, name), 'w', encoding='cp1252', newline='\r\n') as f:
        f.write('BEGIN;\n' + '\n'.join(lines) + '\nCOMMIT;\n')
print('ok')
