import sqlite3, sys, re
db = sys.argv[1]
dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
names = set()
for t in loc.values():
    names.update(re.findall(r'\bPa[a-z]{3,}', t))
print(sorted(n for n in names if len(n) > 5 and n.lower().startswith(('pal','pan','par','pel'))))
print()
for r in s.execute("select * from _Template_Weapon where Id like '%unique%' or Id like '%special%' order by TaAttr"):
    info = loc.get(r['InfoIdentified'], '').replace('\n', ' / ')
    print(f"{loc.get(r['LookAtText'], r['Id'])} [{r['TaAttr']}] {r['WpW6']}d6+{r['WpW6plus']} AT{r['WpATmod']:+} PA{r['WpPAmod']:+} INI{r['WpINI']:+} | {info[:220]}")
