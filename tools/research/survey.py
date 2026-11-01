import sqlite3, sys, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
def conn(n):
    c = sqlite3.connect(f'file:{db}/{n}?mode=ro', uri=True); c.text_factory = dec; return c
s, g, l = conn('static.db4'), conn('game.db4'), conn('locale.db4')
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
eff = collections.Counter(); scr = collections.Counter(); mag = []
for t in [t for (t,) in s.execute("select name from sqlite_master where type='table' and name like '_Template_%'")]:
    cols = [c[1] for c in s.execute(f'pragma table_info([{t}])')]
    if 'PermanentEffect' in cols:
        for (v,) in s.execute(f'select PermanentEffect from [{t}]'):
            for e in (v or '').split(';'):
                if e: eff[e] += 1
    for c in ('ScriptOverride', 'ScriptPreset', 'LimitedScript'):
        if c in cols:
            for (v,) in s.execute(f'select [{c}] from [{t}]'):
                if v: scr[(t[10:], c, v)] += 1
    if 'IsMagical' in cols:
        mag += [(t[10:],) + r for r in s.execute(f'select Id, Graphics from [{t}] where IsMagical=1')]
print('EFFECT CODES', len(eff)); print(sorted(eff))
print('\nSCRIPTS'); [print(' ', k, n) for k, n in sorted(scr.items())]
print('\nIsMagical items', len(mag), mag[:15])
