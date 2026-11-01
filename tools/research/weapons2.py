import sqlite3, sys
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec
l = sqlite3.connect(f'file:{db}/locale.db4?mode=ro', uri=True); l.text_factory = dec
name = lambda k: (l.execute('select LocaText from _Locale where LocaId=?', (k,)).fetchone() or ['?'])[0]
for r in s.execute("select Id, LookAtText, TaAttr, EquipmentType, WpW6, WpW6plus, WpATmod, WpPAmod, WpINI, WpBF, WpReload, Value, Gew, ScriptOverride, PermanentEffect, IconBrush, Graphics from _Template_Weapon where TaAttr<>'' order by TaAttr, Value"):
    print(f"{r[2]:12} {r[0]:42} {name(r[1])[:28]:28} {r[4]}d6+{r[5]:<3} AT{r[6]:+} PA{r[7]:+} INI{r[8]:+} BF{r[9]} rl{r[10]} {r[11]:>6}h {r[12]:>5}g {r[13][-25:]:25} {r[14]:12} {r[15]}")
