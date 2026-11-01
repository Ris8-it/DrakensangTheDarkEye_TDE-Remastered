import sqlite3, sys, re, collections, struct
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
lv = collections.Counter(r[0] for r in g.execute('select _Level from _Instance_NPC'))
names = {k: v for k, v in loc.items() if k.lower().startswith(('location', 'dungeon', 'loc_name', 'levelname'))}
print('LEVELS:', sorted(lv)[:80])
print('level names sample:', list(names.items())[:40])
print('\nINGREDIENTS (bowyer/smith):', [(r[0], loc.get(r[1], '')) for r in s.execute("select Id, LookAtText from _Template_Item where Id like 'zutat_b_%' or Id like 'zutat_s_%'")])
mcols = [c[1] for c in s.execute('pragma table_info(_Template_Monster)')]
print('\nmonster loot cols:', [c for c in mcols if 'oot' in c or 'Stolen' in c or 'Storage' in c])
print('unique NPC rob tables:', [r[0] for r in s.execute("select LootTableName from _DSA_LootTables where LootTableName like 'rob_unique%'")])
bosses = g.execute("select Id, _Level, LootTable from _Instance_Monster where LootTable like '%unique%' or LootTable like '%boss%' limit 30").fetchall() if 'LootTable' in [c[1] for c in g.execute('pragma table_info(_Instance_Monster)')] else []
print('boss loot:', [tuple(b) for b in bosses])
