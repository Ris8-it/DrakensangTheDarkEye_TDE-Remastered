"""Build mods/armory: 90 tiered items, Wyrm upgrade, arrow ladder, custom status effects, icons.

Usage: python -I tools/build_armory.py "<game>/export/db" mods/armory
Reads the game's own rows (read-only). Run against DBs WITHOUT this mod installed (Uninstall first).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, U, lit, mods_text, procs_text, make_icon, NATIVE_OK
from armory_data import STATUS, ITEMS, WYRM, AMMO, D

db, out = sys.argv[1], sys.argv[2]
ICONS_VANILLA = os.path.join(os.path.dirname(__file__), 'research', 'out', 'icons_vanilla')
ICONS_LOOSE = os.path.join(db, '..', 'textures', 'icons')
m = Mod(db, 'armory')
TIER_VALUE = {'regular': D(8), 'amazing': D(15), 'superrare': D(12), 'legendary': D(3)}
TIER_NAME = {'regular': 'Regular', 'amazing': 'Amazing', 'superrare': 'Super rare', 'legendary': 'Legendary'}
IMM = {'fire': 'Immune to burning', 'overthrown': 'Immune to knockdown', 'poison': 'Immune to poison',
       'crowdcontrol': 'Immune to fear, sleep and paralysis', 'cold': 'Immune to cold'}
AURA = {'AttributoMU_State': 'golden', 'Favilludo_State': 'spark', 'Falkenauge_State': "falcon's-eye", 'AttributoKL_State': 'astral',
        'Seidenzunge_State': 'silver', 'Kampf_Offensiv1': 'battle', 'Armatrutz_State': 'Armatrutz', 'Eiseskaelte_State': 'frost-blue',
        'AttributoKO_State': 'ember', 'Psychostabilis_State': 'violet'}
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
icon_files = []

def icon(key, base_brush, tier, tint):
    # Artist-authored overrides are already encoded; keep their original colours.
    custom = os.path.join(os.path.dirname(__file__), '..', 'assets', 'armory_icons_v1', f'arm_{key}.dds')
    if os.path.isfile(custom):
        import shutil
        fname = f'arm_{key}.dds'
        shutil.copy2(custom, os.path.join(out, 'icons', fname))
        icon_files.append(fname)
        return f'icons/arm_{key}'
    name = base_brush.split('/')[-1] + '.dds'
    src = next((p for p in (os.path.join(ICONS_VANILLA, name), os.path.join(ICONS_LOOSE, name)) if os.path.exists(p)), None)
    if not src: print('  no icon for', base_brush, '-> keeping vanilla'); return base_brush
    fname = f'arm_{key}'
    make_icon(src, os.path.join(out, 'icons', fname + '.dds'), tier, tint)
    icon_files.append(fname + '.dds')
    return f'icons/{fname}'

# ---- status effects ----
for sid, name, desc, start, dur, ticks, se, hp, tex, cat, imm in STATUS:
    m.status(sid, name, desc, start=start, duration=dur, ticks=ticks, state_effect=se, hardpoint=hp, texture=tex, categories=cat, immunity=imm)

def check_ids(procs):
    for p in procs:
        if p[0] in ('p', 'if', 'race', 'ifnot'):
            if p[0] in ('if', 'ifnot'): assert p[1] in NATIVE_OK or p[1] in m.se_names, p
            check_ids(p[2])
        elif p[0] == 'st': assert p[1] in NATIVE_OK or p[1] in m.se_names, f'status {p[1]} cannot be created by scripts'
        elif p[0] == 'buff': assert p[1] in m.se_names, p

def effect_lines(it):
    lines = procs_text(it['hit'], m.se_names)
    if it['mods']: lines.append(mods_text(it['mods']))
    for x in filter(None, it['imm'].split(';')): lines.append(IMM[x])
    if it['aura']: lines.append(f"{AURA.get(it['aura'][0], 'faint')} aura while worn".capitalize())
    return lines

# ---- items ----
catalogue = []
for it in ITEMS:
    key, typ = it['key'], it['type']
    iid = f'arm_{key}'
    check_ids(it['hit'])
    base = dict(m.s.execute(f"select * from _Template_{typ} where Id=?", (it['base'],)).fetchone())
    over = dict(it['stats'])
    lines = effect_lines(it)
    desc = it['flavor'] + '\\n\\nEffect: ' + '\\n'.join(lines) if lines else it['flavor']
    pe = ''
    if it['mods'] or it['imm'] or it['aura']:
        se, hp = it['aura'] or ('', '')
        pe = m.status(f'PeArm_{key}', it['name'], '; '.join(lines[len(procs_text(it['hit'], m.se_names)):]) or it['name'],
                      start=it['mods'], state_effect=se, hardpoint=hp, immunity=it['imm'].replace(';', ';'))
    over['PermanentEffect'] = pe
    if 'ScriptOverride' in base: over['ScriptOverride'] = m.hit_script(f'arm_{key}', it['hit']) if it['hit'] else ''
    over['Value'] = it['value'] or TIER_VALUE[it['tier']]
    over['IconBrush'] = icon(key, base['IconBrush'], it['tier'], it['tint'])
    if typ == 'Weapon': over['IsMagical'] = 1
    m.template(typ, it['base'], iid, it['name'], desc, **over)
    places = it['place'] if isinstance(it['place'], list) else [it['place']]
    where = []
    for pl in places:
        if pl[0] == 'loot': m.loot(pl[1], typ, iid, mode=pl[2]); where.append(('loot', pl[1], None))
        else: m.place(typ, iid, pl[0], pl[1], pl[2], stack=it['stack']); where.append(pl)
    catalogue.append((it, lines, where))

# ---- Wyrm upgrade (vanilla templates) ----
wyrm_pe = m.status('PeArm_wyrm', 'Wyrm-touched', 'Immune to burning.', immunity='fire', texture='status_fx_good_fire')
wyrm_rows = []
for wid, wname, hit, stats in WYRM:
    check_ids(hit)
    so = m.hit_script(f'arm_wyrm_{wid}', hit)
    m.edit_vanilla('Weapon', wid, ScriptOverride=so, PermanentEffect=wyrm_pe, **{k: v + m.s.execute(f'select {k} from _Template_Weapon where Id=?', (wid,)).fetchone()[0] for k, v in stats.items()})
    key = m.s.execute('select InfoIdentified from _Template_Weapon where Id=?', (wid,)).fetchone()[0]
    old = m.l.execute('select LocaText from _Locale where LocaId=?', (key,)).fetchone()[0]
    lines = procs_text(hit, m.se_names) + (['Parry +1'] if stats else []) + ['Immune to burning']
    m.vanilla_text(key, old.split('\\n\\nEffect')[0] + '\\n\\nEffect: ' + '\\n'.join(lines))
    wyrm_rows.append((wname, lines))

# ---- arrow ladder ----
ammo_rows = []
for key, base, name, flavor, hit, batch, ingr, diff, (seller, lvl), price in AMMO:
    check_ids(hit)
    aid, rid = f'arm_{key}', f'arm_rezept_{key}'
    b = dict(m.s.execute('select * from _Template_Ammo where Id=?', (base,)).fetchone())
    lines = procs_text(hit, m.se_names)
    m.template('Ammo', base, aid, name, flavor + '\\n\\nEffect: ' + '\\n'.join(lines), ScriptOverride=m.hit_script(aid, hit),
               Value=max(2, price // 4), IsMagical=0, IconBrush=icon(key, b['IconBrush'], 'amazing' if diff >= 12 else 'regular', None))
    names = []
    for part in ingr.strip(';').split(';'):
        _, iid2, n = part.split('/')
        lk = m.s.execute("select LookAtText from _Template_Item where Id=?", (iid2,)).fetchone()[0]
        nm = m.l.execute("select LocaText from _Locale where LocaId=?", (lk,)).fetchone()[0]
        names.append(f'{n} {nm}')
    rdesc = f"Bowcraft {diff}. Makes {batch} {name}.\\nNeeds: " + ', '.join(names)
    m.template('Recipe', 'rezept_kriegspfeile', rid, f'Instructions for {name}', rdesc, RecipeIngredients=ingr,
               RecipeResult=f'Ammo/{aid}/{batch}', Difficulty=diff, Value=D(price))
    m.place('Recipe', rid, 'npc', seller, lvl)
    ammo_rows.append((name, lines, batch, diff, seller, lvl, price))
# a small starting stock of the first two
m.place('Ammo', 'arm_am_barbed_arrow', 'npc', 'Jaeger_Kauzenstein', 'location01', stack=20)
m.place('Ammo', 'arm_am_barbed_bolt', 'npc', 'Zwerg_Zivilist_01_loc02_trainer_graf_armbrust', 'location02_grafenstadt', stack=20)

m.check_collisions()
m.write(out)
with open(os.path.join(out, 'icons', 'files.txt'), 'w') as f: f.write('\n'.join(icon_files) + '\n')

# ---- README catalogue ----
AREA = {'location01': 'Avestrue', 'dungeon01_muehle': 'Avestrue, the old mill', 'dungeon01_baerenhoehle': "Avestrue, bear cave",
        'location02_grafenstadt': "Ferdok, Count's Town", 'location02_praios': 'Ferdok, Praios Square', 'location02_hafen': 'Ferdok, Ugdan Harbour',
        'location02_fuhrmannsheim': "Ferdok, Wagoner's Home", 'dungeon02_diebesgilde': "Ferdok, Thieves' Guild (Cellar Vault)",
        'dungeon02_kanalisation': 'Ferdok, sewers', 'dungeon02_orakel': 'Ferdok, the Oracle dungeon', 'dungeon02_ungluecksrabe': 'Ferdok, Unglücksrabe',
        'dungeon02_residenz': "Ferdok, Ducal Citadel", 'dungeon02_hauptquartier': 'Ferdok, your house (headquarters)',
        'location03': 'Blood Mountains', 'dungeon03_gutshaus_kueche': 'Blood Mountains, manor kitchen', 'dungeon03_blutberge': 'Blood Mountains, cultist dungeon',
        'location04': 'Moorbridge Marshes', 'dungeon04_gruft': 'Moorbridge Crypts', 'dungeon04_baumhoehle': 'Moorbridge, tree cave',
        'dungeon05_burg': 'Silver Falls, Castle Vaults', 'dungeon05_burghof': 'Silver Falls, castle courtyard',
        'location08': 'Tallon', 'dungeon08_gruft_01': 'Tallon Crypt', 'dungeon08_bestie': 'Tallon, Stinking Caves', 'dungeon08_haendler': "Tallon, the trader's ruin",
        'location08_drachenhort': "Dragon's Lair", 'location09': 'Murolosh', 'dungeon09_koenig': 'Murolosh, Throne Room',
        'location10': 'Deeps of Gruldur', 'location11': 'Behind the Fire Falls', 'location12': 'Drakensang Mountain'}
LOOT_WHERE = {'loot_unique_Mantra_keh_03_Noldrokon': ('dungeon05_burghof', "Noldrokon's loot (Mantra'keh chief)"),
              'loot_loc04_skelett_sitzend': ('dungeon04_baumhoehle', 'seated skeleton'), 'loot_unique_Loc03DaVanyaMantraKe': ('location03', "Mantra'keh at Da Vanya's (loot)"),
              'loot_unique_Aldessia_feindlich': ('dungeon09_koenig', "Aldessia's loot"),
              'loot_dun03_truhe_jost': ('dungeon03_blutberge', "Jost's chest"), 'loot_loc05_truhe_drachenraum_02': ('dungeon05_burg', 'dragon-room chest 2 (lock 8)'),
              'loot_loc05_truhe_drachenraum_04': ('dungeon05_burg', 'dragon-room chest 4 (lock 16)'),
              'truhe_verschlossen_01_loc05_geheim_endstueck': ('dungeon05_burg', 'secret chest (end piece)'),
              'truhe_verschlossen_01_loc05_geheim_alchemi': ('dungeon05_burg', 'secret alchemist chest'),
              'loot_loc04_truhe_3': ('location04', 'marsh chest 3 (lock 6)'), 'loot_loc08_truhe_ogerlager_01': ('location08', 'ogre camp chest 1'),
              'loot_loc10_geheimraum_02': ('location10', 'secret room 2'), 'loc08a_truhe_arom': ('location08_drachenhort', "Arom's chest"),
              'loot_loc12_chest_hammerhoehle': ('location12', 'Hammer Cave chest'), 'loot_loc12_chest_durchgang': ('location12', 'passage chest (lock 15)'),
              'loot_loc08_bestie_truhe_leiche_04': ('dungeon08_bestie', 'corpse 4'), 'loot_loc08_haendler_truhe_04': ('dungeon08_haendler', 'chest 4 (lock 10)')}
def where_text(w):
    if w[0] == 'loot': lvl, h = LOOT_WHERE[w[1]]; return f'{AREA.get(lvl, lvl)}: {h}'
    kind, oid, lvl = w
    return f"{AREA.get(lvl, lvl)}: {'sold by' if kind == 'npc' and m.g.execute('select RetailFactor from _Instance_NPC where Id=? and _Level=?', (oid, lvl)).fetchone()[0] else ('carried by' if kind == 'npc' else 'chest')} `{oid}`"
md = ['# Armory', '', 'Item expansion for Drakensang. **Needs a new game** (or a patched save). Install with `Install.bat`, remove with `Uninstall.bat`.', '',
      'Built by `tools/build_armory.py` from `tools/armory_data.py`. Run the **Phase 0b** checks first (mods/phase0b_retest), because some effects rely on them.', '']
for tier in ('regular', 'amazing', 'superrare', 'legendary'):
    rows = [c for c in catalogue if c[0]['tier'] == tier]
    md += [f'## {TIER_NAME[tier]} ({len(rows)})', '', '| Item | Type | Effects | Where |', '|---|---|---|---|']
    for it, lines, where in rows:
        md.append(f"| **{it['name']}** | {it['type']} ({it['base']}) | {'; '.join(lines) or '—'} | {'<br>'.join(where_text(w) for w in where)} |")
    md.append('')
md += ['## Wyrm upgrade (crafted Wyrm weapons)', '', '| Weapon | New effects |', '|---|---|'] + [f'| {n} | {"; ".join(l)} |' for n, l in wyrm_rows] + ['']
md += ['## Arrow ladder (Bowcraft recipes)', '', '| Ammo | Effect | Batch | Bowcraft | Recipe sold by | Price |', '|---|---|---|---|---|---|'] + \
      [f'| {n} | {"; ".join(l)} | {b} | {d} | {AREA.get(lv, lv)} `{s}` | {p} D |' for n, l, b, d, s, lv, p in ammo_rows] + ['']
md += ['## Custom effects', '', '| Effect | What it does |', '|---|---|'] + [f'| {n} | {d} |' for _, n, d, *_ in STATUS] + ['']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('items', len(ITEMS), 'templates', len(m.templates), 'placed', len(m.instances), 'loot entries', len(m.loot_edits),
      'status', len(m.se_names), 'icons', len(icon_files), 'static rows', len(m.static))
