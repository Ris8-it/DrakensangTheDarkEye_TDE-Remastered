import sqlite3, sys
db = sys.argv[1]
dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec; s.row_factory = sqlite3.Row
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
g = sqlite3.connect(f'file:{db}/game.db4?mode=ro', uri=True); g.text_factory = dec; g.row_factory = sqlite3.Row
loc = dict(l.execute('select LocaId, LocaText from _Locale'))
for r in s.execute("select * from _Template_Weapon where Id like '%crafted_unique%' or Id like '%gotterdammerung%' or Id in ('Nachtwind','Andergaster','weapon_crafted_zwergenskraja','weapon_unique_streitaxt')"):
    print('==', loc.get(r['LookAtText'], r['Id']), f"[{r['TaAttr']}]", f"TP {r['WpW6']}d6+{r['WpW6plus']}", f"AT{r['WpATmod']:+} PA{r['WpPAmod']:+} INI{r['WpINI']:+} BF{r['WpBF']} DK {r['WpDK']} reload {r['WpReload']} eff={r['PermanentEffect']}")
    print('  ', loc.get(r['InfoIdentified'], '').replace('\n', ' / ')[:600])
cols = [c[1] for c in g.execute('pragma table_info(_Instance_Weapon)')]
print('instance cols:', [c for c in cols if c.startswith(('Wp','Pe','Perm','Mod','Bonus','Effect'))])
