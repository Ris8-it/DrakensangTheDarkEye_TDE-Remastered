import sqlite3, sys, re, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
def block(gid, ind='    ', depth=0):
    if not gid or gid == bytes(16) or depth > 4: return
    for r in s.execute('select StatementGUID, StatementType, StatementContent from _Scripts_Statements where StatementBlockGUID=? order by rowid', (gid,)):
        print(ind + f"[{r[1]}] {r[2][:260]}")
def action(name):
    for r in s.execute('select * from _Scripts_ActionScripts where ScriptName=?', (name,)):
        print('== ACTION', name); block(r['StatementBlock'])
# 1 Soulsplitter + other on-hit scripts
for n in ('weapon_on_scripts.xml_zauberstab', 'weapon_on_scripts.xml_magiscal_sword', 'weapon_on_scripts.xml_traldars_sword', 'weapon_on_scripts.xml_nasreddins_waquiff', 'weapon_on_scripts.xml_gotterdammerung', 'chargeble_burn.xml', 'weapon_on_scripts.xml_generic_dmg_3'):
    action(n)
print('soulsplitter template:', [dict(r) for r in s.execute("select Id, ScriptOverride, PermanentEffect from _Template_Weapon where ScriptOverride!=''")])
# 2 action vocabulary
verbs = collections.Counter()
for (c,) in s.execute("select StatementContent from _Scripts_Statements where StatementType='Action'"):
    for v in re.findall(r'(?:^|; )([A-Z][A-Za-z]+) ', c or ''): verbs[v] += 1
print('\nACTION VERBS', len(verbs)); print(sorted(verbs))
fx = collections.Counter(re.findall(r'PlayVisualEffect effect="([^"]+)"', ' '.join(c for (c,) in s.execute("select StatementContent from _Scripts_Statements") if c)))
print('\nVISUAL FX', len(fx)); print(sorted(fx))
casts = sorted(set(re.findall(r'(CastSpell[^;]{0,200})', ' '.join(c for (c,) in s.execute("select StatementContent from _Scripts_Statements") if c))))[:10]
print('\nCAST examples', casts)
