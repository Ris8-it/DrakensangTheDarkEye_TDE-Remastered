import sqlite3, sys
db = sys.argv[1]
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True)
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True)
l.text_factory = lambda b: b.decode('cp1252', 'replace')
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
s.row_factory = sqlite3.Row
rows = s.execute("select * from _Template_Weapon where IsMagical=1 or Value>=1500 or PermanentEffect not in ('', 'NONE') order by TaAttr, Value desc").fetchall()
for r in rows:
    name = loc.get(r['Name'], r['Name'])
    tp = f"{r['WpW6']}d6+{r['WpW6plus']}"
    print(f"{r['TaAttr']:<16} {name[:34]:<34} TP {tp:<7} KK {r['WpTPKK1']}/{r['WpTPKK2']} AT{r['WpATmod']:+} PA{r['WpPAmod']:+} INI{r['WpINI']:+} BF{r['WpBF']} val {r['Value']} mag={r['IsMagical']} eff={r['PermanentEffect']} | {r['Id']}")
