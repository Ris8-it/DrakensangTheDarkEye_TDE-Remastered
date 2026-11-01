"""Generate the Ravenwing Saber mod SQL from the game's own rows (read-only)."""
import sqlite3, sys, os, uuid
db, out = sys.argv[1], sys.argv[2]
dec = lambda b: b.decode('cp1252', 'replace')
def conn(name):
    c = sqlite3.connect(f'file:{db}/{name}?mode=ro', uri=True); c.text_factory = dec; c.row_factory = sqlite3.Row; return c
s, g = conn('static.db4'), conn('game.db4')

ITEM = 'ravenwing_saber'
stats = dict(Id=ITEM, Name=ITEM, LookAtText=f'lookat_{ITEM}', InfoIdentified=f'infoid_{ITEM}',
             WpW6=1, WpW6plus=6, WpTPKK1=11, WpTPKK2=3, WpATmod=1, WpPAmod=0, WpINI=1, WpBF=1,
             Gew=1500, Value=3000, PermanentEffect='PeAE10')
texts = {f'lookat_{ITEM}': 'Ravenwing Saber',
         f'infoid_{ITEM}': "A slender saber of dark Maraskan steel, 'liberated' from a Horasian battle mage by the finest hands of the Dark Eye. Faint runes along the fuller channel astral power into its bearer, and it is light enough to fight beside a shield.\n\nEffect: AE +10"}

def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, bytes): return "X'" + v.hex().upper() + "'"
    if isinstance(v, (int, float)): return repr(v)
    return "'" + str(v).replace("'", "''") + "'"
def insert(table, row):
    cols = list(row.keys())
    return f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(lit(row[c]) for c in cols)});"

tmpl = dict(s.execute("select * from _Template_Weapon where Id='Amazonensaebel'").fetchone()); tmpl.update(stats)
static_sql = [f"DELETE FROM _Template_Weapon WHERE Id='{ITEM}';", insert('_Template_Weapon', tmpl)]

game_sql, undo_sql = [], []
base_inst = dict(g.execute("select * from _Instance_Weapon where Id='Magierrapier' and StorageGUID=(select Guid from _Instance_NPC where Id='Cuano_var_nach_loc05')").fetchone())
for i, npc in enumerate(('Cuano', 'Cuano_var_nach_loc05')):
    npc_guid = g.execute('select Guid from _Instance_NPC where Id=?', (npc,)).fetchone()[0]
    row = dict(base_inst)
    for k in tmpl:
        if k in row: row[k] = tmpl[k]
    row['Guid'] = uuid.uuid5(uuid.NAMESPACE_URL, f'drakensang/{ITEM}/{npc}').bytes
    row['StorageGUID'] = npc_guid
    game_sql.append(f"-- {npc}: add only if not already present")
    game_sql.append(f"UPDATE _Instance_NPC SET StorageContentCount=StorageContentCount+1 WHERE Id='{npc}' AND NOT EXISTS (SELECT 1 FROM _Instance_Weapon WHERE Guid={lit(row['Guid'])});")
    game_sql.append(insert('_Instance_Weapon', row).replace('INSERT INTO', 'INSERT OR IGNORE INTO'))
    undo_sql.append(f"UPDATE _Instance_NPC SET StorageContentCount=StorageContentCount-1 WHERE Id='{npc}' AND EXISTS (SELECT 1 FROM _Instance_Weapon WHERE Guid={lit(row['Guid'])});")
    undo_sql.append(f"DELETE FROM _Instance_Weapon WHERE Guid={lit(row['Guid'])};")

locale_sql = [f"INSERT OR REPLACE INTO _Locale (LocaId, LocaText) VALUES ({lit(k)}, {lit(v)});" for k, v in texts.items()]
files = {'static.sql': static_sql, 'locale.sql': locale_sql, 'game.sql': game_sql,
         'undo_static.sql': [f"DELETE FROM _Template_Weapon WHERE Id='{ITEM}';"],
         'undo_locale.sql': [f"DELETE FROM _Locale WHERE LocaId IN ({','.join(lit(k) for k in texts)});"],
         'undo_game.sql': undo_sql}
os.makedirs(out, exist_ok=True)
for name, lines in files.items():
    with open(os.path.join(out, name), 'w', encoding='cp1252', newline='\r\n') as f:
        f.write('BEGIN;\n' + '\n'.join(lines) + '\nCOMMIT;\n')
print('written', sorted(files))
