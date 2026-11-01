import sqlite3, sys, re
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
print([t for (t,) in s.execute("select name from sqlite_master where type='table' and (name like '_Script%' or name like '_DSA%')")])
# condition grammar: find statements whose GUID is referenced by magical_axe's Condition
r = s.execute("select StatementContent from _Scripts_Statements where StatementType='Condition' and StatementContent like '%%' limit 1").fetchone()
for t in ('Condition',):
    rows = s.execute("select StatementGUID, StatementBlockGUID, StatementContent from _Scripts_Statements where StatementType=? limit 3", (t,)).fetchall()
    for row in rows: print(t, row[0].hex() if isinstance(row[0], bytes) else row[0], row[2][:200])
types = s.execute("select StatementType, count(*) from _Scripts_Statements group by 1").fetchall(); print('types', types)
for row in s.execute("select StatementType, StatementContent from _Scripts_Statements where StatementType not in ('Action','Begin','If','Then','Else','Condition') limit 8"): print(' ', row[0], row[1][:200])
for row in s.execute("select StatementContent from _Scripts_Statements where StatementContent like '%Random%' or StatementContent like '%Chance%' limit 6"): print(' RAND', row[0][:200])
# debuffs
print('\nSTATUS EFFECTS (non-permanent):')
for r in s.execute("select Id, State_Categories, State_Effect, Name from _Template_Statuseffects where State_Categories not like '%permanentEffect%'"):
    print(f"  {r['Id']:<28} {loc.get(r['Name'], '')[:28]:<28} {r['State_Categories'][:60]:<60} {r['State_Effect']}")
