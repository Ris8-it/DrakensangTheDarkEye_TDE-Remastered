import sqlite3, sys, re, collections
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
atoms = collections.Counter(re.match(r'(\w+)', r[0]).group(1) for r in s.execute("select ConditionContent from _Scripts_Conditions where ConditionType='Atom'") if r[0] and re.match(r'(\w+)', r[0]))
print('CONDITION ATOMS', sorted(atoms))
for r in s.execute("select ConditionContent from _Scripts_Conditions where ConditionContent like '%Random%' or ConditionContent like '%Chance%' or ConditionContent like '%Percent%' limit 5"): print('  ', r[0])
for r in s.execute("select LootTableName, LootTableContent from _DSA_LootTables where LootTableName in ('rob_unique_cuano','rob_unique_rakorium','rob_mensch_mittel')"): print('ROB', r[0], r[1][:250])
print('\nPRICES:')
for t, q in (('Armor', "Id like '%zwerg%' and Value>3000"), ('Weapon', "Id in ('Amazonensaebel','Langschwert','Kurzbogen','Langbogen','Andergaster','Felsspalter')"), ('Jewelry', "Value>=1000")):
    for r in s.execute(f"select Id, LookAtText, Value from _Template_{t} where {q} order by Value desc limit 8"): print(f'  {t:<8} {loc.get(r[1], r[0])[:34]:<34} {r[2]}')
print('\nPARTY:')
for pid in ('pc_rhulana', 'pc_gwendala', 'pc_forgrimm', 'pc_dranor', 'pc_cano', 'pc_ardo'):
    r = g.execute('select * from _Instance_PC where Id=?', (pid,)).fetchone()
    if not r: continue
    ta = {k: r[k] for k in r.keys() if (k.startswith('Ta') or k.startswith('SF_') or k.startswith('Za')) and isinstance(r[k], int) and r[k] > 0 and k not in ('TargetSize',)}
    top = sorted(ta.items(), key=lambda x: -x[1])[:14]
    print(f" {pid} {r['Profession']} lvl {r['Stufe']} MU{r['MU']} KL{r['KL']} IN{r['IN']} CH{r['CH']} FF{r['FF']} GE{r['GE']} KO{r['KO']} KK{r['KK']} AE{r['AEmax']} | {top}")
print([r[0] for r in g.execute("select Id from _Instance_PC")])
