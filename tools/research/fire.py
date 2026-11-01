import sqlite3, sys
db = sys.argv[1]
dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
for r in s.execute("select * from _Template_Weapon order by TaAttr"):
    info = loc.get(r['InfoIdentified'], '')
    if 'Algormosh' not in info: continue
    print(f"== {loc.get(r['LookAtText'])} | {r['Id']} [{r['TaAttr']}] {r['WpW6']}d6+{r['WpW6plus']} KK {r['WpTPKK1']}/{r['WpTPKK2']} AT{r['WpATmod']:+} PA{r['WpPAmod']:+} INI{r['WpINI']:+} BF{r['WpBF']} DK {r['WpDK']} reload {r['WpReload']} wt {r['Gew']} eff={r['PermanentEffect']}")
    print('   ', info.replace('\n', ' / '))
print([ (k,v[:200]) for k,v in loc.items() if 'Algormosh' in v and 'infoid' not in k][:15])
