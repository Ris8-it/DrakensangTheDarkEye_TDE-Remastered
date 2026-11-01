import sqlite3, sys
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec
for t in ('_Template_Statuseffects', '_Scripts_StatusEffectScripts', '_Scripts_Statements', '_Script_StateMachines'):
    try:
        cols = [c[1] for c in s.execute(f'pragma table_info([{t}])')]
        n = s.execute(f'select count(*) from [{t}]').fetchone()[0]
        print('##', t, n, cols)
    except Exception as e: print(t, e)
print([r for r in s.execute("select * from _Template_Statuseffects where Id like 'Pe%' or Id like '%AE%' limit 8")])
r = s.execute("select * from _Scripts_StatusEffectScripts limit 3").fetchall(); print(r)
for k in ('PeAE10', 'schleifstein', 'waffenbalsam', 'generic_dmg_2', 'tenobaal', 'TatzeSchwinge'):
    hits = []
    for (t,) in s.execute("select name from sqlite_master where type='table'").fetchall():
        for c in [c[1] for c in s.execute(f'pragma table_info([{t}])')]:
            try: n = s.execute(f"select count(*) from [{t}] where [{c}] like ?", (f'%{k}%',)).fetchone()[0]
            except Exception: continue
            if n: hits.append((t, c, n))
    print(k, hits)
