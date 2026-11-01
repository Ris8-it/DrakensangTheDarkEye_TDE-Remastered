"""Hard Ending (optional): tougher late-game enemies and bosses. Multiplies the CURRENT values (stacks with other balance mods).
Usage: python -I tools/build_hard_ending.py "<game>/export/db/armory_backup" mods/hard_ending
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod
db, out = sys.argv[1], sys.argv[2]
# build on top of the core pack's boss toughening (remastered_systems, tools/beasts_data.py): a scratch copy of the baseline with
# that module applied, so Hard Ending scales the toughened values and its uninstall restores them, not the vanilla ones
import shutil, sqlite3, tempfile
_snap = tempfile.mkdtemp()
for _d in ('static', 'locale', 'game'):
    shutil.copy2(os.path.join(db, f'{_d}.db4'), _snap)
    _sql = os.path.join(os.path.dirname(__file__), '..', 'mods', 'remastered_systems', 'sql', f'{_d}.sql')
    if _d != 'locale' and os.path.exists(_sql):
        _c = sqlite3.connect(os.path.join(_snap, f'{_d}.db4')); _c.text_factory = lambda b: b.decode('cp1252', 'replace')
        _c.executescript(open(_sql, encoding='cp1252').read()); _c.commit(); _c.close()
m = Mod(_snap, 'hardending')
LATE = re.compile(r'(loc09|loc10|loc11|loc12|dungeon09|drachenhort)', re.I)
BOSS = {  # id: (LE factor, AT, PA, MR, armour, extra immunities)
    'Purpurdrache': (2.5, 3, 2, 3, 2, 'fire;overthrown;stun'), 'Japhgur': (2.5, 3, 2, 3, 2, 'fire;overthrown;stun'),
    'Malgorra_loc12': (2.0, 3, 3, 5, 2, 'overthrown;stun'), 'Zyklopenskelett_loc10': (1.4, 3, 2, 3, 2, ''),
    'Oger_04_kraeftig_loc08_boss': (1.5, 3, 2, 2, 1, ''), 'Arombolosch_Wahnsinn': (1.6, 3, 3, 4, 1, 'overthrown'),
    'Aldessia_feindlich': (1.8, 3, 3, 4, 1, ''), 'gruftassel_boss_loc09': (1.6, 2, 0, 2, 1, ''),
}
ZONES = ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')
rows = []
for typ in ('Monster', 'NPC'):
    cols = {c[1] for c in m.s.execute(f'pragma table_info(_Template_{typ})')}
    for r in m.s.execute(f'select * from _Template_{typ}'):
        r = dict(r); iid = r['Id']
        if iid in BOSS: f, at, pa, mr, rs, imm = BOSS[iid]
        elif LATE.search(iid) and (r['LEmax'] or 0) >= 40 and r.get('Faction', '') not in ('FaPlayer', 'FaAllFriendly', 'FaFreund'): f, at, pa, mr, rs, imm = 1.3, 2, 2, 2, 1, ''
        else: continue
        new = {'LEmax': int(round(r['LEmax'] * f)), 'LE': int(round((r['LE'] or r['LEmax']) * f)), 'AT': r['AT'] + at, 'PA': r['PA'] + pa, 'MR': (r['MR'] or 0) + mr}
        for z in ZONES:
            if z in cols and (r[z] or 0) > 0: new[z] = r[z] + rs
        if imm and 'Immunity' in cols:
            new['Immunity'] = ';'.join(dict.fromkeys([x for x in (r['Immunity'] or '').split(';') if x] + imm.split(';')))
        new = {k: v for k, v in new.items() if k in cols and v != r[k]}
        if new:
            m.edit_vanilla(typ, iid, **new)
            rows.append((typ, iid, r['LEmax'], new.get('LEmax', r['LEmax']), new.get('Immunity', '')))
# the real boss fights are LARGE monsters (separate table): Japhgur in his lair (1125 LE) and Malgorra's dragon form (1500 LE).
# Tallon's Linnorm is not "late" and stays vanilla. (balance audit A12)
LARGE = {'Japhgur': (1.3, 2, 1, 'overthrown'), 'loc12_finale_Malgorra_Monster': (1.3, 2, 1, '')}
lcols = {c[1] for c in m.s.execute('pragma table_info(_Template_MonsterLarge)')}
for iid, (f, at, rs, imm) in LARGE.items():
    r = dict(m.s.execute('select * from _Template_MonsterLarge where Id=?', (iid,)).fetchone())
    new = {'LEmax': int(round(r['LEmax'] * f)), 'LE': int(round(r['LE'] * f)), 'AT': r['AT'] + at}
    for z in ZONES:
        if z in lcols and (r[z] or 0) > 0: new[z] = r[z] + rs
    if imm: new['Immunity'] = ';'.join(dict.fromkeys([x for x in (r['Immunity'] or '').split(';') if x] + imm.split(';')))
    m.edit_vanilla('MonsterLarge', iid, **new)
    rows.append(('MonsterLarge', iid, r['LEmax'], new['LEmax'], new.get('Immunity', '')))
m.write(out)
os.makedirs(os.path.join(out, 'icons'), exist_ok=True); open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
md = ['# Hard Ending (optional)', '', 'Tougher late-game enemies (Murolosh, Gruldur, Fire Falls, Drakensang Mountain, the Dragon\'s Lair) and bosses.',
      'Multiplies current values: LE x1.3, AT/PA +2, MR +2, armour +1 for late enemies; bosses more (table). The real dragon fights (Japhgur in his lair, the dragon form of Malgorra) are large monsters and get LE x1.3, AT +2, armour +1. The `Purpurdrache`/`Japhgur` Monster rows are the small overworld/cutscene dragons. New game recommended.', '',
      '| Type | Id | LE before | LE after | Immunities |', '|---|---|---|---|---|'] + [f'| {t} | {i} | {a} | {b} | {c} |' for t, i, a, b, c in rows]
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('edited', len(rows), 'bosses', sum(1 for r in rows if r[1] in BOSS))
