"""Every pack weapon (found, sold or crafted) with its effective damage against the vanilla curve of its stage.

    python -I tools/maint/weapon_audit.py     (after power_curve.py; needs .work/new_full)

Effective damage = average dice damage + the average of on-hit damage procs (chance x amount). Attribute bonuses and AT/PA are
listed separately. Vanilla uniques given by quests (Pal'Na'Thar fire weapons, Wyrm weapons, Dragonslayer hammer) don't show in
shop data: their values are listed at the end for scale.
"""
import os, re, sys, sqlite3
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.dirname(__file__))
from power_curve import availability, stage_of, STAGE_NAMES, curve, avg, vs   # reuses the vanilla curve (prints nothing extra)
import armory_data as AD
first, how, s, g = availability(os.path.join(ROOT, '.work', 'new_full'))

def proc_avg(hit):
    tot = 0.0
    for kind, p, acts in [h for h in hit if h[0] == 'p']:
        for a in acts:
            if a[0] == 'dmg': tot += p / 100 * (a[1] + 3.5 * a[2])
    return tot

made_at = {}
for rid, res in s.execute("select Id, RecipeResult from _Template_Recipe where Id like 'arm_%'"):
    st = [stage_of(l, o) for l, o in g.execute('select i._Level, coalesce(n.Id,"") from _Instance_Recipe i left join _Instance_NPC n on n.Guid=i.StorageGUID where i.Id=?', (rid,))]
    st = [x for x in st if x is not None]
    if st: made_at[res.split('/')[1]] = min(st)
rows = []
for it in AD.ITEMS:
    if it['type'] != 'Weapon': continue
    iid = f"arm_{it['key']}"
    r = s.execute('select TaAttr, WpW6, WpW6plus, WpATmod, WpPAmod, WpINI from _Template_Weapon where Id=?', (iid,)).fetchone()
    if not r: continue
    ta, w6, plus, at, pa, ini = r
    st = min([x for x in (first.get(iid), made_at.get(iid), it.get('stage')) if x is not None], default=None)
    eff = avg(w6, plus) + proc_avg(it['hit'])
    best = max((v[0] for s2, v in curve.get(ta, {}).items() if st is not None and s2 <= st), default=0)
    attrs = ' '.join(x for x in re.findall(r'(?:KK|GE|FF|MU|KO|KL|IN|CH|AT|PA|AW) [+-]\d+', it.get('mods', '')))
    rows.append((st if st is not None else 9, ta, it['tier'], it['name'], f'{w6}W6+{plus}', at, pa, eff, best, attrs, iid))
rows.sort()
print('| Stage | Talent | Tier | Weapon | Dice | AT/PA | Effective | Vanilla best then | Gap | Attributes |')
print('|---|---|---|---|---|---|---|---|---|---|')
for st, ta, tier, name, dice, at, pa, eff, best, attrs, iid in rows:
    gap = eff - best if best else 0
    print(f"| {STAGE_NAMES[st] if st < 9 else 'quest/none'} | {ta} | {tier} | {name} | {dice} | {at:+}/{pa:+} | {eff:.1f} | {best:.1f} | {gap:+.1f}{' !' if gap > 1.5 else ''} | {attrs} |")
print('\nVanilla quest uniques for scale:')
for iid, in s.execute("select Id from _Template_Weapon where Id like 'weapon_unique_%' or Id like 'weapon_crafted_unique_%' or Id like '%drachentoeter%'"):
    r = vs.execute('select TaAttr, WpW6, WpW6plus, WpATmod from _Template_Weapon where Id=?', (iid,)).fetchone()
    if r and r[1]: print(f'  {iid}: {r[0]} {r[1]}W6+{r[2]} ({avg(r[1], r[2]):.1f}) AT{r[3]:+}')
