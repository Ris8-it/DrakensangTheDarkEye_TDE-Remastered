"""Power curve: what the unmodded game hands out at each story stage, and where the pack's craftables sit against it.

    python -I tools/maint/power_curve.py      (needs .work/new_full = baseline + all modules installed; build_all/obtainable make it)

Stages follow the story, not the level number:
  0 Avestrue | 1 Ferdok | 2 Dark Forest / Moorbridge | 3 Grimmzahn + Ferdok stock "after Grimmzahn" | 4 Tallon | 5 Murolosh | 6 Gruldur | 7 Fire Falls
Writes .work/power_curve.md (tables) and prints a short summary.
"""
import os, re, sys, sqlite3, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
VAN = os.path.join(GAME, 'export', 'db', 'armory_backup'); NEW = os.path.join(ROOT, '.work', 'new_full')
STAGE_NAMES = ['Avestrue', 'Ferdok', 'DarkForest/Moorbridge', 'Grimmzahn', 'Tallon', 'Murolosh', 'Gruldur', 'FireFalls']
dec = lambda b: b.decode('cp1252', 'replace')

def stage_of(level, owner=''):
    n = re.search(r'(?:location|dungeon|loc|dun)_?(\d\d)', level or '')
    if not n: return None
    n = int(n.group(1))
    st = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 7}.get(n)
    if st is not None and re.search(r'nach_?loc05', owner or ''): st = max(st, 3)
    if st is not None and re.search(r'nach_?loc0[89]', owner or ''): st = max(st, 4)
    return st

def availability(dbdir):
    """earliest stage per item id (shops, chests, carried loot, loot tables; debug chests excluded)"""
    g = sqlite3.connect(os.path.join(dbdir, 'game.db4')); g.text_factory = dec
    s = sqlite3.connect(os.path.join(dbdir, 'static.db4')); s.text_factory = dec
    first, how = {}, {}
    def seen(iid, st, what):
        if st is None: return
        if st < first.get(iid, 99): first[iid] = st; how[iid] = what
    for t in ('_Instance_Weapon', '_Instance_Armor', '_Instance_Shield', '_Instance_Jewelry', '_Instance_Ammo', '_Instance_Recipe', '_Instance_Item'):
        for iid, lvl, owner, chest in g.execute(f"""select i.Id, i._Level, coalesce(n.Id, ''), coalesce(c.Id, '') from "{t}" i
                left join _Instance_NPC n on n.Guid = i.StorageGUID left join _Instance_Chest c on c.Guid = i.StorageGUID"""):
            if chest.startswith('debug'): continue
            seen(iid, stage_of(lvl, owner), ('shop ' + owner) if owner else ('chest ' + chest))
    for name, c in s.execute('select LootTableName, LootTableContent from _DSA_LootTables'):
        for e in (c or '').split(';'):
            if e.count('/') >= 2: seen(e.split('/')[1], stage_of(name), 'loot ' + name)
    return first, how, s, g

vf, vhow, vs, vg = availability(VAN)
nf, nhow, ns, ng = availability(NEW)
out = []
P = out.append

# ---------- weapons: best average damage per talent and stage (vanilla) ----------
W = {r[0]: r[1:] for r in vs.execute('select Id, TaAttr, WpW6, WpW6plus, WpATmod, WpPAmod, WpINI, Value from _Template_Weapon')}
avg = lambda w6, plus: 3.5 * (w6 or 0) + (plus or 0)
curve = collections.defaultdict(dict)
for iid, st in vf.items():
    if iid in W and W[iid][0]:
        ta, w6, plus, at, pa, ini, val = W[iid]
        d = avg(w6, plus)
        if d > curve[ta].get(st, (0,))[0]: curve[ta][st] = (d, iid, f'{w6}W6+{plus}', at, pa)
P('# Vanilla weapon curve: best average damage per talent and stage\n')
P('| Talent | ' + ' | '.join(STAGE_NAMES) + ' |'); P('|---' * 9 + '|')
for ta in sorted(curve):
    best, row = 0, []
    for st in range(8):
        if st in curve[ta]: best = max(best, curve[ta][st][0])
        row.append(f'{curve[ta][st][2]} ({curve[ta][st][0]:.1f})' if st in curve[ta] else (f'({best:.1f})' if best else ''))
    P(f'| {ta} | ' + ' | '.join(row) + ' |')

# ---------- armour: best total protection per slot and stage (vanilla) ----------
Z = ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')
A = {r[0]: (r[1], r[2], sum(r[3:11]), r[11]) for r in vs.execute(f'select Id, EquipmentType, ArMaterial, {",".join(Z)}, ArBE from _Template_Armor')}
acurve = collections.defaultdict(dict)
for iid, st in vf.items():
    if iid in A:
        eq, mat, rs, be = A[iid]
        k = (eq, mat)
        if rs > acurve[k].get(st, (0,))[0]: acurve[k][st] = (rs, iid, be)
P('\n# Vanilla armour curve: best total protection (8 zones) per slot/material and stage (encumbrance)\n')
P('| Slot | Material | ' + ' | '.join(STAGE_NAMES) + ' |'); P('|---' * 10 + '|')
for (eq, mat) in sorted(acurve):
    row, best = [], 0
    for st in range(8):
        c = acurve[(eq, mat)].get(st)
        if c: best = max(best, c[0])
        row.append(f'{c[0]} ({c[2]:.1f})' if c else (f'·{best}' if best else ''))
    P(f'| {eq} | {mat} | ' + ' | '.join(row) + ' |')

# ---------- pack craftables against the curve ----------
import armory_data as AD
items = {f"arm_{it['key']}": it for it in AD.ITEMS}
P('\n# Pack plans: result vs. base vs. the vanilla best at the stage the plan is sold\n')
P('| Plan | Sold at (stage) | Result | Kind | Base -> result | Bonuses | vs vanilla best then | Ingredients |'); P('|---' * 8 + '|')
flags = []
for rid, ing, res, diff in ns.execute("select Id, RecipeIngredients, RecipeResult, Difficulty from _Template_Recipe where Id like 'arm_%' order by Id"):
    rtyp, riid = res.split('/')[:2]
    sellers = [(stage_of(l, o), o) for l, o in ng.execute('select i._Level, coalesce(n.Id, "") from _Instance_Recipe i left join _Instance_NPC n on n.Guid = i.StorageGUID where i.Id=?', (rid,))]
    st = min((x[0] for x in sellers if x[0] is not None), default=None)
    it = items.get(riid, {})
    base = next((p.split('/')[1] for p in (ing or '').split(';') if p.count('/') >= 2 and p.split('/')[0] in ('Weapon', 'Armor', 'Shield', 'Jewelry')), None)
    kind, cmp, change = rtyp, '', ''
    if rtyp == 'Weapon':
        r = ns.execute('select TaAttr, WpW6, WpW6plus, WpATmod, WpPAmod from _Template_Weapon where Id=?', (riid,)).fetchone()
        if r:
            ta, w6, plus, at, pa = r
            b = ns.execute('select WpW6, WpW6plus, WpATmod, WpPAmod from _Template_Weapon where Id=?', (base,)).fetchone() if base else None
            change = (f'{b[0]}W6+{b[1]} AT{b[2]:+} PA{b[3]:+} -> ' if b else '') + f'{w6}W6+{plus} AT{at:+} PA{pa:+}'
            kind = ta
            if st is not None and ta in curve:
                best = max((v[0] for s2, v in curve[ta].items() if s2 <= st), default=0)
                d = avg(w6, plus); cmp = f'{d:.1f} vs {best:.1f}'
                if best and d > best + 1: flags.append(f'{rid}: {ta} {d:.1f} avg at {STAGE_NAMES[st]}, vanilla best {best:.1f}')
    elif rtyp == 'Armor':
        r = ns.execute(f'select EquipmentType, ArMaterial, {",".join(Z)}, ArBE from _Template_Armor where Id=?', (riid,)).fetchone()
        if r:
            eq, mat, rs, be = r[0], r[1], sum(r[2:10]), r[10]
            b = A.get(base) if base else None
            change = (f'{b[2]} ({b[3]:.1f}) -> ' if b else '') + f'{rs} ({be:.1f})'
            kind = f'{eq}/{mat}'
            if st is not None and (eq, mat) in acurve:
                best = max((v[0] for s2, v in acurve[(eq, mat)].items() if s2 <= st), default=0)
                cmp = f'{rs} vs {best}'
                if best and rs > best + 1: flags.append(f'{rid}: {eq}/{mat} protection {rs} at {STAGE_NAMES[st]}, vanilla best {best}')
            if base and base in vf and st is not None and vf[base] > st:
                flags.append(f'{rid}: base {base} first available {STAGE_NAMES[vf[base]]} in vanilla, plan sold {STAGE_NAMES[st]}')
    mods = it.get('mods', '') + (' imm:' + it['imm'] if it.get('imm') else '')
    ingr = ', '.join(p.split('/')[1] + ' x' + p.split('/')[2] for p in (ing or '').split(';') if p.count('/') >= 2)
    P(f"| {rid[11:]} | {STAGE_NAMES[st] if st is not None else 'dialog/none'} | {it.get('name', riid)} | {kind} | {change} | {mods} | {cmp} | {ingr} |")

# ---------- talents that don't belong on gear ----------
P('\n# Gear bonuses to review (Survival, Animal Lore, Plant Lore, Brawling)\n')
bad = re.compile(r'TaWildnisleben|TaTierkunde|TaPflanzenkunde|TaRaufen')
for it in AD.ITEMS:
    if bad.search(it.get('mods', '')): P(f"- arm_{it['key']} ({it['type']}, {it['tier']}): {it['name']}: {it['mods']}")
open(os.path.join(ROOT, '.work', 'power_curve.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(flags))
print(f'{len(flags)} flags; full tables in .work/power_curve.md')
