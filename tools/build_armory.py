"""Build Armory v2: tiered items, crafting upgrades, dragon materials, Wyrm and Pal'Na'Thar weapon upgrades, icons.

Usage: python -I tools/build_armory.py "<game>/export/db/armory_backup" mods/armory_v2
Read-only on the source DBs. Always build from the clean armory_backup folder.

Tooltip rule (review R04): weapons, armour and shields get ONLY native permanent effects, composed exactly
from their bonuses; anything non-native on them is a build error. Jewelry may use custom effects (its
tooltip lists none) and auras.
"""
import sys, os, re, shutil
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, mods_text, procs_text, make_icon, NATIVE_OK, FOE, Block, U, lit, insert, pack_names
PACK_NAMES = pack_names(os.path.join(os.path.dirname(__file__), '..'))
from armory_data import armour_rules, item_stage
ARMOUR_LOG = []
from armory_data import (STATUS, ITEMS, MATERIALS, HOARD_EXTRA, FEATHER_STOCK, BASE_STOCK, WYRM, CYCLOPS, VANILLA_PE, AMMO, D, TOOL_STOCK, RECIPE_EASE, SETS_V24, ELFWOOD_STOCK, TEMPERED, WAGNITZ_DROP)

db, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(__file__)
ICONS_VANILLA = os.path.join(HERE, 'research', 'out', 'icons_vanilla')
ART = [os.path.join(HERE, '..', 'assets', d) for d in ('armory_icons_v2', 'armory_icons_v1')]   # reviewed custom art, newest first
m = Mod(db, 'armory')
TIER_VALUE = {'regular': D(8), 'amazing': D(15), 'superrare': D(12), 'legendary': D(3), 'mythic': D(2)}
TIER_NAME = {'regular': 'Regular', 'amazing': 'Amazing', 'superrare': 'Super rare', 'legendary': 'Legendary', 'mythic': 'Mythic'}
SKILL = {'TaSchmieden': 'Smithing', 'TaBogenbau': 'Bowcraft', 'TaAlchimie': 'Alchemy', 'TaMagiekunde': 'Arcane lore'}
RECIPE_BASE = {'TaSchmieden': 'rezept_verbessertes_kurzschwert', 'TaBogenbau': 'rezept_verbesserter_langbogen'}
IMM_NATIVE = {'fire': 'PeNotBurnable', 'overthrown': 'PeImmuneToKnockdown', 'poison': 'PeImmuneToPoison1'}
AURA_NAME = {'AttributoMU_State': 'Golden aura', 'Favilludo_State': 'Spark aura', 'Falkenauge_State': "Falcon's-eye aura", 'AttributoKL_State': 'Astral aura',
             'Seidenzunge_State': 'Silver aura', 'Kampf_Offensiv1': 'Battle aura', 'Armatrutz_State': 'Armatrutz aura', 'Eiseskaelte_State': 'Frost aura',
             'AttributoKO_State': 'Ember aura', 'Psychostabilis_State': 'Violet aura', 'Axxeleratus_State': 'Quicksilver aura'}
IMM_TEXT = {'fire': 'immune to burning', 'overthrown': 'immune to knockdown', 'poison': 'immune to poison', 'crowdcontrol': 'immune to fear, sleep and paralysis'}
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
icon_files = []

# ---------- native effect catalogue (read from the game, vanilla + mg979 permanent effects) ----------
NATIVE = {}   # pid -> {attr: value}
for pid, sb in m.s.execute("select t.Id, c.StatusEffectOnStartBlock from _Template_Statuseffects t join _Scripts_StatusEffectScripts c on c.Id=t.Id "
                           "where t.State_Categories like '%permanentEffect%' and t.State_Immunity='' and t.State_Effect=''"):
    acts = [r[0] for r in m.s.execute("select StatementContent from _Scripts_Statements where StatementBlockGUID=? and StatementType='Action'", (sb,))] if sb else []
    if len(acts) != 1 or not acts[0].startswith('ModifyAttribute'): continue
    mods = dict((a, int(sg + n)) for a, sg, n in re.findall(r'(\w+) ([+-])(\d+)', re.search(r'modifier="([^"]*)"', acts[0]).group(1)))
    if mods and not pid.startswith(('PeCyclope', 'PeValon', 'PeLongKnife', 'Dom2', 'Nat2', 'Sne2', 'PeElven', 'PeHelm', 'PeAll')):
        NATIVE[pid] = mods
def compose(mods):
    """Exact decomposition of 'A +n B +m' into native effect ids (multi-attribute ones first). Returns (ids, leftover dict)."""
    want = {a: int(sg + n) for a, sg, n in re.findall(r'(\w+) ([+-])(\d+)', mods)}
    ids = []
    for pid, eff in sorted(NATIVE.items(), key=lambda kv: (-len(kv[1]), -sum(kv[1].values()), kv[0])):
        if all(v > 0 and want.get(a, 0) >= v for a, v in eff.items()):
            ids.append(pid)
            for a, v in eff.items():
                want[a] -= v
                if not want[a]: del want[a]
    return ids, want

def icon(key, base_brush, tier, tint):
    for d in ART:
        custom = os.path.join(d, f'arm_{key}.dds')
        if os.path.isfile(custom):
            shutil.copy2(custom, os.path.join(out, 'icons', f'arm_{key}.dds')); icon_files.append(f'arm_{key}.dds')
            return f'icons/arm_{key}', os.path.basename(d)
    src = os.path.join(ICONS_VANILLA, base_brush.split('/')[-1] + '.dds')
    if not os.path.exists(src): src = os.path.join('D:/Steam/steamapps/common/Drakensang/export/textures/icons', base_brush.split('/')[-1] + '.dds')
    if not os.path.exists(src): print('  no icon for', base_brush); return base_brush, 'vanilla'
    make_icon(src, os.path.join(out, 'icons', f'arm_{key}.dds'), tier, tint)
    icon_files.append(f'arm_{key}.dds')
    return f'icons/arm_{key}', 'tinted'

# ---------- status effects ----------
for sid, name, desc, start, dur, ticks, se, hp, tex, cat, imm in STATUS:
    m.status(sid, name, desc, start=start, duration=dur, ticks=ticks, state_effect=se, hardpoint=hp, texture=tex, categories=cat, immunity=imm)
def check_ids(procs):
    for p in procs:
        if p[0] in ('p', 'if', 'race', 'ifnot'):
            if p[0] in ('if', 'ifnot'): assert p[1] in NATIVE_OK or p[1] in m.se_names, p
            check_ids(p[2])
        elif p[0] == 'st': assert p[1] in NATIVE_OK or p[1] in m.se_names, f'status {p[1]} cannot be created by scripts'
        elif p[0] == 'buff': assert p[1] in m.se_names, p

def stat_line(typ, t):
    """Vanilla-style compact stat line for recipe previews."""
    if typ == 'Weapon':
        s = f"{t['WpW6']}D6{t['WpW6plus']:+d} HP"
        for k, n in (('WpATmod', 'AT'), ('WpPAmod', 'PA'), ('WpINI', 'INI')):
            if t[k]: s += f", {n} {t[k]:+d}"
        if t['WpReload']: s += f", reload {t['WpReload']} CR"
        return s
    if typ == 'Armor':
        z = [('Head', 'RSKo'), ('Chest', 'RSBr'), ('Belly', 'RSBa'), ('Back', 'RSRu'), ('Arms', 'RSLA'), ('Legs', 'RSLB')]
        mat = {'Metal': 'metal', 'Leather': 'leather', 'Cloth': 'cloth'}.get(t['ArMaterial'], t['ArMaterial'])
        return ', '.join(f'{n} {t[k]}' for n, k in z if t[k]) + f'; {mat}, encumbrance {round(t["ArBE"], 1)}'
    if typ == 'Shield': return f"AT {t['WpATmod']:+d}, PA {t['WpPAmod']:+d}"
    return ''

def item_name(typ, iid):
    if f'lookat_{iid}' in m.locale: return m.locale[f'lookat_{iid}']      # pack items (balance audit B13: no raw Ids in recipe tooltips)
    if iid.startswith('arm_'): return PACK_NAMES.get(iid, iid)              # items of other pack modules (e.g. remastered trophies)
    lk = m.s.execute(f'select LookAtText from _Template_{typ} where Id=?', (iid,)).fetchone()
    return m.l.execute('select LocaText from _Locale where LocaId=?', (lk[0],)).fetchone()[0] if lk else iid

# ---------- crafting material ----------
for key, base, name, desc, value, places in MATERIALS:
    iid = f'arm_{key}'
    b = dict(m.s.execute('select * from _Template_Item where Id=?', (base,)).fetchone())
    br, src = icon(key, b['IconBrush'], 'superrare', (200, 90, 255))
    m.template('Item', base, iid, name, desc, Value=value, IconBrush=br)
    for kind, oid, lvl, n in places: m.place('Item', iid, kind, oid, lvl, stack=n)
for typ, iid, n in HOARD_EXTRA: m.place(typ, iid, 'chest', 'loc08a_truhe_japhgur', 'location08_drachenhort', stack=n, tag='extra')
# v2.7: plans found instead of sold, boss relics, and bosses that get their own loot table (old loot + relic)
from armory_data import LOOT_EXTRA, LOOT_OWN
for _table, _typ, _iid in LOOT_EXTRA: m.loot(_table, _typ, _iid, mode='all')
for (_typ, _oid), _extra in LOOT_OWN.items():
    _cur = m.s.execute(f'select LootTable from _Template_{_typ} where Id=?', (_oid,)).fetchone()[0] or ''
    _old = [e for e in m.loot_tables().get(_cur, ('0', ''))[1].split(';') if e]
    _name = f'arm_lt_own_{_oid}'
    _content = ''.join(e + ';' for e in _old) + ''.join(f'{t}/{i}/{c}/{n}/1/;' for t, i, c, n in _extra)
    m.static += [f'DELETE FROM _DSA_LootTables WHERE LootTableName={lit(_name)};',
                 f'INSERT INTO _DSA_LootTables (LootTableName, LootTableValue, LootTableContent) VALUES ({lit(_name)}, {lit(str(len(_old) + len(_extra)))}, {lit(_content)});']
    m.undo_static.append(f'DELETE FROM _DSA_LootTables WHERE LootTableName={lit(_name)};')
    m.edit_vanilla(_typ, _oid, LootTable=_name)
for oid, lvl, n in FEATHER_STOCK: m.place('Item', 'zutat_b_harpyienfedern', 'npc', oid, lvl, stack=n, tag='feathers')
_seen = {}
for typ, iid, oid, lvl in BASE_STOCK:   # a second copy at the same shop needs its own tag (the first keeps the old GUID)
    k = _seen[(iid, oid)] = _seen.get((iid, oid), -1) + 1
    m.place(typ, iid, 'npc', oid, lvl, tag='basestock' if k == 0 else f'basestock{k}')
for typ, iid, oid, lvl in TOOL_STOCK: m.place(typ, iid, 'npc', oid, lvl, tag='toolstock')
# Elf wood: vanilla has no source at all (balance audit A1); give it a price and a supply
m.edit_vanilla('Item', 'zutat_b_elfenholz', Value=600, IconBrush='icons/bogenbau_zutat_elfenholz')   # vanilla left it on the dummy icon
for e in ELFWOOD_STOCK:
    if e[0] == 'loot': m.loot(e[1], 'Item', 'zutat_b_elfenholz', mode='all', amount=e[2])
    else: m.place('Item', 'zutat_b_elfenholz', 'npc', e[1], e[2], stack=e[3], tag='elfwood')

# ---------- heirloom set bonuses (v2.4): one permanent effect per heirloom stage ----------
# Start script: for each set piece, if the party owns it -> per-piece bonus, else a no-op modifier (every If needs an Else);
# then, if all four are owned -> the full-set bonus. Same HasItem check as the proven remastered set bonuses (Phase 0b B11).
SETPE, SETLINE = {}, {}
for hkey, (pieces, per, full, label) in SETS_V24.items():
    pid = 'PeArmSet' + ''.join(w.capitalize() for w in hkey.split('_'))
    st = Block(f'armory/se/{pid}/start')
    has = lambda iid: f'HasItem owner="PlayerParty" templateId="{iid}" category="Armor" amount="1"; '
    act = lambda b, x: b.action(f'ModifyAttribute modifier="{x}" actionSelection="script"; ')
    NOOP = 'TaSinnenschaerfe +0'
    kids = [st.if_(has(p), lambda b=st: [act(b, per)], build_else=lambda b=st: [act(b, NOOP)]) for p in pieces]
    if full:
        def chain(i, b=st):
            if i == len(pieces): return [act(b, full)]
            return [b.if_(has(pieces[i]), lambda: chain(i + 1), build_else=lambda: [act(b, NOOP)])]
        kids += chain(0)
    st.begin(kids)
    tr = Block(f'armory/se/{pid}/trigger'); tr.begin([tr.action('WaitAction duration="1" permanent="true" actionSelection="script"; ')])
    m.emit_block(st); m.emit_block(tr)
    Z = bytes(16); sg = U('armory', 'se', pid)
    m.static.append(insert('_Scripts_StatusEffectScripts', dict(Guid=sg, Id=pid, Name='', StatusEffectOnStartRef=st.ref, StatusEffectOnStartBlock=st.guid,
        StatusEffectOnTriggerRef=tr.ref, StatusEffectOnStopRef=Z, StatusEffectOnTriggerBlock=tr.guid, StatusEffectOnStopBlock=Z,
        StatusEffectCategories='', StatusEffectTexture='', StatusEffectStackable=1, StatusEffectPower=1)))
    text = f"Set ({label}): {mods_text(per)} for each piece you own" + (f"; all four: {mods_text(full)}" if full else '') + ' (re-equip after finding a piece)'
    m.static.append(insert('_Template_Statuseffects', dict(Id=pid, State_Effect='', State_Hardpoint='', State_Sound='', State_Texture='textures:icons/status_fx_good_jewel.dds',
        State_Categories='permanentEffect', Name=f'{pid}_name', ShortDescription=f'{pid}_name', LongDescription=f'{pid}_name', State_Immunity='')))
    m.undo_static += [f"DELETE FROM _Scripts_StatusEffectScripts WHERE Guid={lit(sg)};", f"DELETE FROM _Template_Statuseffects WHERE Id={lit(pid)};"]
    m.text(f'{pid}_name', text); m.new_guids.append(sg); m.se_names[pid] = text
    SETPE[hkey], SETLINE[hkey] = pid, text


# Bows and crossbows never run on-hit scripts (the player tested it, 3 Nov: no 15 % procs, no bonus damage; the arrow carries the hit).
# Their effects are folded into what does work: expected bonus damage becomes flat damage, any status effect becomes +1 ranged attack.
RANGED = ('TaBogen', 'TaArmbrust')
def ranged_fold(base, hit, over):
    """For a bow/crossbow: returns [] and puts the value of `hit` into over (WpW6plus, WpATmod). Other weapons: hit unchanged."""
    if base.get('TaAttr') not in RANGED or not hit: return hit
    acc = {'dmg': 0.0, 'status': False}
    def walk(entries, mult):
        for e in entries:
            if e[0] == 'p': walk(e[2], mult * e[1] / 100.0)
            elif e[0] == 'if': walk(e[2], mult * 0.25)
            elif e[0] == 'dmg': acc['dmg'] += mult * (e[1] + 3.5 * e[2])
            else: acc['status'] = True
    walk(hit, 1.0)
    bonus = int(acc['dmg'] + 0.5) or (1 if acc['dmg'] >= 0.3 else 0)
    if bonus: over['WpW6plus'] = over.get('WpW6plus', base['WpW6plus']) + bonus
    if acc['status']: over['WpATmod'] = (over.get('WpATmod', base['WpATmod']) or 0) + 1
    RANGED_LOG.append((base['Id'], round(acc['dmg'], 1), acc['status']))
    return []
RANGED_LOG = []
# ---------- items ----------
catalogue, recipes = [], []
for it in ITEMS:
    key, typ = it['key'], it['type']
    iid = f'arm_{key}'
    check_ids(it['hit'])
    base = dict(m.s.execute(f"select * from _Template_{typ} where Id=?", (it['base'],)).fetchone())
    over = dict(it['stats'])
    if typ == 'Weapon': it['hit'] = ranged_fold(base, it['hit'], over)
    if typ == 'Armor':
        _note = armour_rules(base, over, item_stage(it))
        if _note: ARMOUR_LOG.append((iid, it['tier'], item_stage(it), _note))
        assert base['GfxSkin'] not in {'schuhe_elfen', 'schuhe_gwendala', 'schuhe_lederstiefel_04', 'schuhe_lederstiefel_05', 'schuhe_lederstiefel_06'}, key
    # permanent effects
    native_ids, left = compose(it['mods'])
    imms = [x for x in it['imm'].split(';') if x]
    custom_imm = [x for x in imms if x not in IMM_NATIVE]
    # native effects first (vanilla tooltip lines); the rest in ONE custom effect with a letters-only Id (underscores break tooltips)
    left_mods = ' '.join(f"{a} {v:+d}" for a, v in left.items())
    ids = native_ids + [IMM_NATIVE[x] for x in imms if x in IMM_NATIVE]
    if left_mods or custom_imm or it['aura']:
        se, hp = it['aura'] or ('', '')
        label = '; '.join(filter(None, [mods_text(left_mods) if left_mods else '', ', '.join(IMM_TEXT[x] for x in custom_imm).capitalize(),
                                        (AURA_NAME.get(se, 'Aura') if se else '')])) or it['name']
        ids.append(m.status('PeArm' + ''.join(w.capitalize() for w in key.split('_')), label, label, start=left_mods,
                            state_effect=se, hardpoint=hp, immunity=';'.join(custom_imm)))
    if key in SETPE: ids.append(SETPE[key])
    pe = ';'.join(ids)
    over['PermanentEffect'] = pe
    if 'ScriptOverride' in base: over['ScriptOverride'] = m.hit_script(f'arm_{key}', it['hit']) if it['hit'] else ''
    over['Value'] = it['value'] or TIER_VALUE[it['tier']]
    over['IconBrush'], art = (base['IconBrush'], 'vanilla') if it.get('vanilla_icon') else icon(key, base['IconBrush'], it['tier'], it['tint'])
    if typ == 'Weapon': over['IsMagical'] = 1
    # compact tooltip: lore, bonuses, then conditional procs
    passive = ([mods_text(it['mods'])] if it['mods'] else []) + [IMM_TEXT[x].capitalize() for x in imms]
    lines = passive + procs_text(it['hit'], m.se_names) + ([SETLINE[key]] if key in SETLINE else [])
    desc = it['flavor'] + ('\\n\\n' + '\\n'.join(lines) if lines else '')
    t = m.template(typ, it['base'], iid, it['name'], desc, **over)
    where = []
    places = it['place'] if isinstance(it['place'], list) else ([it['place']] if it['place'] else [])
    for pl in places:
        if pl[0] == 'loot': m.loot(pl[1], typ, iid, mode=pl[2]); where.append(('loot', pl[1], None))
        else: m.place(typ, iid, pl[0], pl[1], pl[2], stack=it['stack']); where.append(pl)
    # crafting recipe
    r = it['recipe']
    if r:
        rid = f'arm_rezept_{key}'
        diff = max(3, r['diff'] - RECIPE_EASE)
        batch = it.get('batch') or (10 if it['stack'] > 1 else 1)
        ingr = ''.join(f'{ty}/{bid}/{n};' for ty, bid, n in r['consumes']) + ''.join(f'Item/{mid}/{n};' for mid, n in r['mats'])
        consumed = ', '.join([f'{n} {item_name(ty, bid)}' for ty, bid, n in r['consumes']] + [f'{n} {item_name("Item", mid)}' for mid, n in r['mats']])
        source = ('\\nUNIQUE: the original cannot be bought again.' if r['final'] else
                  '\\nThe source item can be bought again.' if r['consumes'] else '')
        preview = (f"{SKILL[r['skill']]} {diff}. Makes {str(batch) + ' ' if batch > 1 else ''}{it['name']}.\\n{stat_line(typ, t)}"
                   + (f"\\n{'; '.join(lines)}" if lines else '') + f"\\nConsumes: {consumed}." + source)
        rbase = RECIPE_BASE.get(r['skill']) or m.s.execute('select Id from _Template_Recipe where TaAttr=? limit 1', (r['skill'],)).fetchone()[0]
        m.template('Recipe', rbase, rid, f"Plans: {it['name']}", preview, RecipeIngredients=ingr,
                   RecipeResult=f'{typ}/{iid}/{batch}', Difficulty=diff, TaAttr=r['skill'], Value=D(r['price']),
                   IconBrush=m.recipe_icon(typ, iid, r['skill']))
        for oid, lvl in r['sellers']: m.place('Recipe', rid, 'npc', oid, lvl)
        recipes.append((it, dict(r, diff=diff), consumed))
    catalogue.append((it, lines, where, pe, art))

# ---------- vanilla weapon upgrades: Wyrm + Pal'Na'Thar ----------
def upgrade(rows, label):
    done = []
    for wid, wname, hit, deltas in rows:
        check_ids(hit)
        cur = dict(m.s.execute('select * from _Template_Weapon where Id=?', (wid,)).fetchone())
        new = {k: cur[k] + v for k, v in deltas.items()}
        hit = ranged_fold(cur, hit, new)
        pe = ';'.join(x for x in (cur['PermanentEffect'] or '').split(';') + ['PeNotBurnable'] if x)
        pe = ';'.join(dict.fromkeys(pe.split(';')))
        m.edit_vanilla('Weapon', wid, ScriptOverride=m.hit_script(f'arm_{label}_{wid}', hit) if hit else '', PermanentEffect=pe, **new)
        old = m.l.execute('select LocaText from _Locale where LocaId=?', (cur['InfoIdentified'],)).fetchone()[0]
        nd = {**cur, **new}
        lines = [f"{nd['WpW6']}D6{nd['WpW6plus']:+d} HP", 'Immune to burning'] + procs_text(hit, m.se_names)
        m.vanilla_text(cur['InfoIdentified'], re.split(r'\\n\\nEffect', old)[0] + '\\n\\n' + '\\n'.join(lines))
        done.append((wname, lines))
    return done
wyrm_rows = upgrade(WYRM, 'wyrm')
cyclops_rows = upgrade(CYCLOPS, 'cyc')

# ---------- Pal'Na'Thar's tempering (balance audit N2): the chosen Fire weapon, one step further ----------
# Built on the upgraded Fire weapon (CYCLOPS hit + deltas) plus +1 damage, +1 AT and one signature effect. The recipe has no seller:
# Pal'Na'Thar hands over the one matching the Fire weapon you carry (secret_quests). Consumes the weapon and one Heavy Wyrm Scale.
CYC = {w: (n, h, d) for w, n, h, d in CYCLOPS}
temper_rows = []
for wid, key, name, extra, skill in TEMPERED:
    cname, chit, cdel = CYC[wid]
    base = dict(m.s.execute('select * from _Template_Weapon where Id=?', (wid,)).fetchone())
    hit = chit + [extra]; check_ids(hit)
    over = {k: base[k] + v for k, v in cdel.items()}
    over['WpW6plus'] = over.get('WpW6plus', base['WpW6plus']) + 1
    over['WpATmod'] = (base['WpATmod'] or 0) + 1
    hit = ranged_fold(base, hit, over)
    over['ScriptOverride'] = m.hit_script(f'arm_{key}', hit) if hit else ''
    over['PermanentEffect'] = 'PeNotBurnable'
    over['IconBrush'], _art = icon(key, base['IconBrush'], 'mythic', (255, 120, 40))
    over['IsMagical'] = 1; over['Value'] = D(5)
    nd = {**base, **over}
    lines = [f"{nd['WpW6']}D6{nd['WpW6plus']:+d} HP, AT {nd['WpATmod']:+d}", 'Immune to burning'] + procs_text(hit, m.se_names)
    m.template('Weapon', wid, f'arm_{key}', name, f"{cname}, tempered by Pal'Na'Thar in the Last Fire around a scale of Japhgur. "
               "There is no finer blade in Aventuria.\n\n" + '\n'.join(lines), **over)
    rid = f'arm_rezept_{key}'
    rb = RECIPE_BASE[skill]
    m.template('Recipe', rb, rid, f'Plans: {name}', f"{SKILL[skill]} 14. Makes {name}.\n{lines[0]}\n{'; '.join(lines[1:])}"
               f"\nConsumes: {cname}, 1 Heavy Wyrm Scale, 1 Dwarven Steel.\nUNIQUE: given by Pal'Na'Thar; one Fire weapon, one tempering.",
               RecipeIngredients=f'Weapon/{wid}/1;Item/arm_wyrm_scale/1;Item/zutat_s_stahlzwergen/1;', RecipeResult=f'Weapon/arm_{key}/1',
               Difficulty=14, TaAttr=skill, Value=D(1), IconBrush=m.recipe_icon('Weapon', f'arm_{key}', skill))
    temper_rows.append((name, lines))
# ---------- B7: the Spellthief's Dirk drops from the Blood Mountains Wagnitz only (his loot table was shared by three NPCs) ----------
_wn, _wt, _wi = WAGNITZ_DROP
_old = m.loot_tables()[_wt][1]; _oe = [e for e in _old.split(';') if e]
m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_wagnitz_loc03';",
             f"INSERT INTO _DSA_LootTables (LootTableName, LootTableValue, LootTableContent) VALUES ('arm_lt_wagnitz_loc03', '{len(_oe) + 1}', "
             + repr(''.join(e + ';' for e in _oe) + f'Weapon/{_wi}/100/1/0/;').replace('"', "'") + ");"]
m.undo_static.append("DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_wagnitz_loc03';")
m.edit_vanilla('NPC', _wn, LootTable='arm_lt_wagnitz_loc03')
for typ, iid, pe, txt in VANILLA_PE:
    cur = m.s.execute(f'select PermanentEffect, InfoIdentified from _Template_{typ} where Id=?', (iid,)).fetchone()
    m.edit_vanilla(typ, iid, PermanentEffect=';'.join(x for x in (cur[0] or '').split(';') + [pe] if x))

# ---------- arrow ladder ----------
ammo_rows = []
for key, base, name, flavor, hit, batch, ingr, diff, (seller, lvl), price in AMMO:
    check_ids(hit)
    aid, rid = f'arm_{key}', f'arm_rezept_{key}'
    b = dict(m.s.execute('select * from _Template_Ammo where Id=?', (base,)).fetchone())
    lines = procs_text(hit, m.se_names)
    br, _ = icon(key, b['IconBrush'], 'amazing' if diff >= 12 else 'regular', None)
    m.template('Ammo', base, aid, name, flavor + '\\n\\n' + '\\n'.join(lines), ScriptOverride=m.hit_script(aid, hit), Value=max(2, price // 4), IsMagical=0, IconBrush=br)
    names = ', '.join(f"{part.split('/')[2]} {item_name('Item', part.split('/')[1])}" for part in ingr.strip(';').split(';'))
    m.template('Recipe', 'rezept_kriegspfeile', rid, f'Instructions for {name}', f"Bowcraft {diff}. Makes {batch} {name}.\\n{'; '.join(lines)}\\nNeeds: {names}.",
               RecipeIngredients=ingr, RecipeResult=f'Ammo/{aid}/{batch}', Difficulty=diff, Value=D(price))
    if seller: m.place('Recipe', rid, 'npc', seller, lvl)   # no seller: the plan is a unique drop
    if lvl == 'location01': m.place('Recipe', rid, 'npc', 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')
    ammo_rows.append((name, lines, batch, diff, seller, lvl, price))
m.place('Ammo', 'arm_am_barbed_arrow', 'npc', 'Jaeger_Kauzenstein', 'location01', stack=20)
m.place('Ammo', 'arm_am_barbed_arrow', 'npc', 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios', stack=20)
m.place('Ammo', 'arm_am_barbed_bolt', 'npc', 'Zwerg_Zivilist_01_loc02_trainer_graf_armbrust', 'location02_grafenstadt', stack=20)

m.check_collisions()
m.mirror_early()
m.write(out)
shutil.copy2(os.path.join(HERE, 'sql', 'clear_rhulana_tests.sql'), os.path.join(out, 'sql'))
with open(os.path.join(out, 'icons', 'files.txt'), 'w') as f: f.write('\n'.join(icon_files) + '\n')

# ---------- README / catalogue ----------
AREA = {'location01': 'Avestrue', 'dungeon01_muehle': 'Avestrue, old mill', 'location02_grafenstadt': "Ferdok, Count's Town", 'location02_praios': 'Ferdok, Praios Square',
        'location02_hafen': 'Ferdok, harbour', 'location02_fuhrmannsheim': "Ferdok, Wagoner's Home", 'dungeon02_diebesgilde': "Ferdok, Thieves' Guild",
        'dungeon02_kanalisation': 'Ferdok, sewers', 'dungeon02_orakel': 'Ferdok, Oracle', 'dungeon02_ungluecksrabe': 'Ferdok, Unglücksrabe',
        'dungeon02_residenz': 'Ferdok, Ducal Citadel', 'dungeon02_hauptquartier': 'Ferdok, your house', 'location03': 'Blood Mountains',
        'dungeon03_gutshaus_kueche': 'Blood Mountains, manor kitchen', 'dungeon03_blutberge': 'Blood Mountains, cult dungeon', 'location04': 'Moorbridge',
        'dungeon04_gruft': 'Moorbridge Crypts', 'dungeon04_baumhoehle': 'Moorbridge, tree cave', 'dungeon05_burg': 'Silver Falls, Castle Vaults',
        'dungeon05_burghof': 'Silver Falls, courtyard', 'location08': 'Tallon', 'dungeon08_gruft_01': 'Tallon Crypt', 'dungeon08_bestie': 'Tallon, Stinking Caves',
        'dungeon08_haendler': "Tallon, trader's ruin", 'location08_drachenhort': "Dragon's Lair", 'location09': 'Murolosh', 'dungeon09_koenig': 'Murolosh, Throne Room',
        'location10': 'Deeps of Gruldur', 'location11': 'Behind the Fire Falls', 'location12': 'Drakensang Mountain'}
LOOT_WHERE = {'loot_unique_Mantra_keh_03_Noldrokon': ('dungeon05_burghof', "Noldrokon's loot"), 'loot_loc04_skelett_sitzend': ('dungeon04_baumhoehle', 'seated skeleton'),
              'loot_unique_Loc03DaVanyaMantraKe': ('location03', "Mantra'keh at Da Vanya's"), 'loot_unique_Aldessia_feindlich': ('dungeon09_koenig', "Aldessia's loot"),
              'loot_dun03_truhe_jost': ('dungeon03_blutberge', "Jost's chest"), 'loot_loc05_truhe_drachenraum_02': ('dungeon05_burg', 'dragon-room chest 2'),
              'loot_loc05_truhe_drachenraum_04': ('dungeon05_burg', 'dragon-room chest 4 (lock 16)'), 'truhe_verschlossen_01_loc05_geheim_endstueck': ('dungeon05_burg', 'secret end chest'),
              'truhe_verschlossen_01_loc05_geheim_alchemi': ('dungeon05_burg', 'secret alchemist chest'), 'loot_loc04_truhe_3': ('location04', 'marsh chest 3'),
              'loot_loc08_truhe_ogerlager_01': ('location08', 'ogre camp chest'), 'loot_loc10_geheimraum_02': ('location10', 'secret room 2'),
              'loc08a_truhe_arom': ('location08_drachenhort', "Arom's chest"), 'loot_loc12_chest_hammerhoehle': ('location12', 'Hammer Cave chest'),
              'loot_loc12_chest_durchgang': ('location12', 'passage chest (lock 15)'), 'loot_loc08_bestie_truhe_leiche_04': ('dungeon08_bestie', 'corpse 4'),
              'loot_loc08_haendler_truhe_04': ('dungeon08_haendler', 'chest 4 (lock 10)')}
def where_text(w):
    if w[0] == 'loot':
        lvl, h = LOOT_WHERE.get(w[1], ('', w[1].replace('loot_unique_', 'boss loot: ').replace('loot_', '')))
        return f'{AREA.get(lvl, lvl)}: {h}'.lstrip(': ')
    kind, oid, lvl = w
    return f"{AREA.get(lvl, lvl)}: {'sold by' if kind == 'npc' else 'chest'} `{oid}`"
md = ['# Armory v2', '', 'Playtest revision of 30 October 2026 (docs/reviews/2026-10-30). **New game required.**', '',
      'Weapon, armour and shield bonuses use only native effects, so their tooltip lines render like vanilla. Jewelry keeps custom effects.', '']
for tier in ('regular', 'amazing', 'superrare', 'legendary', 'mythic'):
    rows = [c for c in catalogue if c[0]['tier'] == tier]
    md += [f'## {TIER_NAME[tier]} ({len(rows)})', '', '| Item | Type | Effects | Where | Craft | Effects ids | Icon |', '|---|---|---|---|---|---|---|']
    for it, lines, where, pe, art in rows:
        rc = it['recipe']
        craft = f"{SKILL[rc['skill']]} {rc['diff']}{' (unique base)' if rc['final'] else ''}" if rc else ''
        md.append(f"| **{it['name']}** | {it['type']} ({it['base']}) | {'; '.join(lines) or '—'} | {'<br>'.join(where_text(w) for w in where) or 'crafted only'} | {craft} | {pe} | {art} |")
    md.append('')
md += ['## Crafting recipes', '', '| Result | Skill | Consumes | Plans sold by |', '|---|---|---|---|'] + \
      [f"| {it['name']} | {SKILL[r['skill']]} {r['diff']} | {c} | {'<br>'.join(f'{AREA.get(l, l)} `{o}`' for o, l in r['sellers'])} |" for it, r, c in recipes] + ['']
md += ['## Wyrm weapons (upgraded vanilla)', '', '| Weapon | Now |', '|---|---|'] + [f'| {n} | {"; ".join(l)} |' for n, l in wyrm_rows] + ['']
md += ["## Pal'Na'Thar final weapons (upgraded vanilla)", '', '| Weapon | Now |', '|---|---|'] + [f'| {n} | {"; ".join(l)} |' for n, l in cyclops_rows] + ['']
md += ['## Arrow ladder', '', '| Ammo | Effect | Batch | Bowcraft | Plans sold by | Price |', '|---|---|---|---|---|---|'] + \
      [f'| {n} | {"; ".join(l)} | {b} | {d} | {AREA.get(lv, lv)} `{s}` | {p} D |' for n, l, b, d, s, lv, p in ammo_rows] + ['']
md += ['## Dragon hoard and supplies', '', "- Japhgur's hoard: +7 Heavy Wyrm Scales, +1 dragon tooth, +1 dragon sinew, the Splinter of Umbracor's Heart.",
       '- Harpy feathers (finite): ' + ', '.join(f'{n} at {AREA.get(l, l)} `{o}`' for o, l, n in FEATHER_STOCK) + '.',
       '- Extra base stock for recipes: ' + ', '.join(f'{iid} at `{o}`' for _, iid, o, _ in BASE_STOCK) + '.',
       "- Rhulana's Kurkumian Amazon Armor gains Courage +1 (native effect).", '']
md += ['## Custom effects (weapon procs and jewelry)', '', '| Effect | What it does |', '|---|---|'] + [f'| {n} | {d} |' for _, n, d, *_ in STATUS] + ['']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
from collections import Counter
print('ranged folded', len(RANGED_LOG), RANGED_LOG[:3])
print('tiers', dict(Counter(it['tier'] for it in ITEMS)), 'recipes', len(recipes), 'templates', len(m.templates), 'placed', len(m.instances),
      'loot', len(m.loot_edits), 'status', len(m.se_names), 'icons', len(icon_files), 'vanilla edits', len(m.vanilla_edits))

for _r in ARMOUR_LOG: print('armour rule:', *_r)
