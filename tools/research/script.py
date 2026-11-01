import sqlite3, sys
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
print('ActionScripts cols', [c[1] for c in s.execute('pragma table_info(_Scripts_ActionScripts)')])
def block(gid, ind='    '):
    if not gid or gid == bytes(16): return
    for r in s.execute('select StatementType, StatementContent from _Scripts_Statements where StatementBlockGUID=? order by rowid', (gid,)):
        print(ind + f"[{r[0]}] {r[1]}")
def statusfx(name):
    r = s.execute('select * from _Scripts_StatusEffectScripts where Id=?', (name,)).fetchone()
    print('== STATUS', name, {k: r[k] for k in ('StatusEffectCategories','StatusEffectStackable','StatusEffectPower')})
    for part in ('Start', 'Trigger', 'Stop'):
        print('  on', part); block(r[f'StatusEffectOn{part}Block']); block(r[f'StatusEffectOn{part}Ref'])
for n in ('PeAE10', 'PeWpPA2', 'PeHelmOfFlames'): statusfx(n)
for r in s.execute("select * from _Scripts_ActionScripts where ScriptName like '%generic_dmg_2%' or ScriptName like '%tenobaal%' or ScriptName like '%schleifstein%' or ScriptName like '%waffenbalsam%' or ScriptName like '%magical_axe%'"):
    print('== ACTION', {k: (r[k].hex() if isinstance(r[k], bytes) else r[k]) for k in r.keys()})
    for k in r.keys():
        if isinstance(r[k], bytes) and len(r[k]) == 16: block(r[k])
