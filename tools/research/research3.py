import sqlite3, sys, re, uuid
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
for t in ('_Scripts_Conditions', '_Scripts_ConditionScripts', '_DSA_LootTables'):
    print(t, [c[1] for c in s.execute(f'pragma table_info([{t}])')], s.execute(f'select count(*) from [{t}]').fetchone()[0])
# magical_axe condition
a = s.execute("select StatementBlock from _Scripts_ActionScripts where ScriptName='weapon_on_scripts.xml_magical_axe'").fetchone()[0]
for r in s.execute('select StatementGUID, StatementType, StatementContent from _Scripts_Statements where StatementBlockGUID=?', (a,)):
    print(' ', r[1], r[2])
    if r[1] in ('If', 'Condition'):
        for gid in r[2].split(';'):
            try: b = uuid.UUID(gid).bytes_le
            except Exception: continue
            for q in (b, uuid.UUID(gid).bytes):
                for row in s.execute('select * from _Scripts_Conditions where rowid in (select rowid from _Scripts_Conditions where hex(Guid)=?)', (q.hex().upper(),)) if 'Guid' in [c[1] for c in s.execute('pragma table_info(_Scripts_Conditions)')] else []:
                    print('    COND', dict(row))
print([dict(r) for r in s.execute("select * from _Scripts_Conditions limit 4")])
# loot tables
for r in s.execute("select * from _DSA_LootTables limit 3"): print('LOOT', {k: (str(r[k])[:300]) for k in r.keys()})
print('rob tables sample:', [ (r[0], (loc.get(r[0]) or '')) for r in g.execute("select distinct StolenGoodsTable from _Instance_NPC where StolenGoodsTable!='' limit 8")])
print([dict(r) | {'LootTableContent': r['LootTableContent'][:300]} for r in s.execute("select * from _DSA_LootTables where Id like '%cuano%' or Id like 'rob_unique%' limit 2")])
