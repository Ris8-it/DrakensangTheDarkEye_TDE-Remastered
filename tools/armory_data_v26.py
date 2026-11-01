# v2.6 crafting rework (1 Nov, docs/CRAFTING_PLAN.md): five crafting lines, one step per chapter, every step needs hunted parts.
# Exec'd by armory_data.py after armory_data_v25.py (uses its OTTO and the Moonhowl items).
DARK_TRADER = ('Haendlerin_1_loc03_dunkelforst', 'location03')   # Dark Forest village
SAPHIRA = ('Saphira_Trader', 'location03')                        # the witch herbalist's stall
MOOR_SMITH = ('Wirt_2_loc04_schmied', 'location04')
TUSK, CLAW, CRAB, WART, LOUSE, STING, FSAC, SPIDER, TATZEL = (
    'arm_tr_boar_tusk', 'arm_tr_bear_claw', 'arm_tr_crab_plate', 'arm_tr_toad_wart', 'arm_tr_louse_carapace',
    'arm_tr_scorpion_sting', 'arm_tr_firefly_sac', 'arm_tr_spider_eye', 'arm_tr_tatzel_fang')
SILK, HARPY = 'seidendruese', 'zutat_b_harpyienfedern'

ITEMS += [
    # ---- Tusk and Claw: medium leather for the front line. Ch1 Count's Town -> ch2 Moorbridge -> ch3 Tallon ----
    A('tc_cuirass', 'amazing', 'torso_verstaerkte_lederruestung', 'Tuskhide Cuirass',
      'A leather cuirass plated with split boar tusk. Ugly, heavy-shouldered and very hard to cut.',
      None, mods='LEmax +5 TaSelbstbeherrschung +1', RSBr=4, RSRu=4, RSBa=4, RSLA=1, RSRA=1, ArBE=2.0, tint=EARTH,
      recipe=R('TaSchmieden', 7, [('Armor', 'torso_verstaerkte_lederruestung', 1)], [(TUSK, 4), (STRIPS, 2)], [FERDOK_SMITH], 7)),
    A('tc_bracers', 'amazing', 'armschienen_nieten_01', 'Tuskhide Bracers',
      'Studded arm guards with a row of tusk tips down each forearm. Good for blocking, better for brawling.',
      None, mods='TaRaufen +2 AUmax +3', RSLA=3, RSRA=3, ArBE=0.2, tint=EARTH,
      recipe=R('TaSchmieden', 6, [('Armor', 'armschienen_nieten_01', 1)], [(TUSK, 2), (STRIPS, 1)], [FERDOK_SMITH], 5)),
    A('tc_helm', 'amazing', 'helm_verstaerkte_lederruestung', 'Bearclaw Helm',
      'A leather helm with bear claws sewn round the brow like a crown. Enemies look at the claws, not at you.',
      None, mods='TaEinschuechtern +2 AUmax +3', RSKo=4, ArBE=0.6, tint=EARTH,
      recipe=R('TaBogenbau', 7, [('Armor', 'helm_verstaerkte_lederruestung', 1)], [(CLAW, 2), (STRIPS, 1)], [OTTO], 5)),
    A('ts_cuirass', 'superrare', 'torso_verstaerkte_lederruestung', 'Ironshell Cuirass',
      'The Tuskhide Cuirass, faced with giant-crab shell over the chest. Blades skid off it like oars off a hull.',
      None, mods='LEmax +8 TaSelbstbeherrschung +2 MR +1', RSBr=5, RSRu=5, RSBa=4, RSLA=1, RSRA=1, ArBE=2.0, tint=EARTH,
      recipe=R('TaSchmieden', 10, [('Armor', 'arm_tc_cuirass', 1)], [(CRAB, 3), (STEEL, 1)], [MOOR_SMITH], 10)),
    A('ts_bracers', 'superrare', 'armschienen_nieten_01', 'Ironshell Bracers',
      'Tuskhide Bracers with crab-shell plates over the wrist. They ring when struck.',
      None, mods='TaRaufen +2 AUmax +5 PA +1', RSLA=4, RSRA=4, ArBE=0.2, tint=EARTH,
      recipe=R('TaSchmieden', 9, [('Armor', 'arm_tc_bracers', 1)], [(CRAB, 2)], [MOOR_SMITH], 8)),
    A('ts_helm', 'superrare', 'helm_verstaerkte_lederruestung', 'Ironshell Helm',
      'The Bearclaw Helm, lined with bitter troll-toad leather and capped with crab shell. Curses taste it and back away.',
      None, mods='TaEinschuechtern +3 MR +1', RSKo=5, ArBE=0.6, tint=EARTH,
      recipe=R('TaSchmieden', 9, [('Armor', 'arm_tc_helm', 1)], [(CRAB, 2), (WART, 1)], [MOOR_SMITH], 8)),
    A('tw_cuirass', 'legendary', 'torso_verstaerkte_lederruestung', 'Warlord Cuirass',
      'Ironshell reinforced with Kosh steel, crypt-louse chitin and a tatzelwurm fang over the heart. You do not fall down any more.',
      None, mods='LEmax +12 MU +1 KK +1', imm='overthrown', RSBr=6, RSRu=6, RSBa=5, RSLA=2, RSRA=2, ArBE=2.0, tint=EARTH,
      recipe=R('TaSchmieden', 13, [('Armor', 'arm_ts_cuirass', 1)], [(TATZEL, 1), (LOUSE, 2), (KOSH, 1)], [TALLON_CRAFT], 14)),
    A('tw_bracers', 'legendary', 'armschienen_nieten_01', 'Warlord Bracers',
      'Ironshell Bracers with hard crypt-louse chitin riveted along the edge. Every parry bites back.',
      None, mods='AT +1 FF +1 AUmax +5', RSLA=5, RSRA=5, ArBE=0.2, tint=EARTH,
      recipe=R('TaSchmieden', 12, [('Armor', 'arm_ts_bracers', 1)], [(LOUSE, 2), (KOSH, 1)], [TALLON_CRAFT], 12)),
    A('tw_helm', 'legendary', 'helm_verstaerkte_lederruestung', 'Warlord Helm',
      'The Ironshell Helm under a Kosh-steel crest. Its wearer is always the one the others look to.',
      None, mods='MU +1 TaEinschuechtern +3 MR +1', RSKo=6, ArBE=0.6, tint=EARTH,
      recipe=R('TaSchmieden', 12, [('Armor', 'arm_ts_helm', 1)], [(CLAW, 2), (KOSH, 1)], [TALLON_CRAFT], 12)),

    # ---- Witch-cloth: casters, no metal. Ch2 Saphira (Dark Forest) -> ch3 Tallon magic trainer -> Dragonblood Robe (Murolosh) ----
    A('ww_robe', 'amazing', 'oberteil_heilmagier', 'Witchweave Robe',
      'A green robe re-woven with spider silk and dyed in troll-toad sap, the way the forest witches do it.',
      None, mods='AEmax +10 MR +1 TaPflanzenkunde +2', RSBr=2, RSRu=2, RSBa=2, RSLA=1, RSRA=1, ArBE=0.0, tint=LEAF,
      recipe=R('TaAlchimie', 8, [('Armor', 'oberteil_heilmagier', 1)], [(SILK, 2), (WART, 2)], [SAPHIRA], 8)),
    A('ww_hood', 'amazing', 'hut_heilmagier', 'Witchweave Hat',
      'A pointed hat stiffened with spider silk. Whatever it hears, it whispers to you.',
      None, mods='AEmax +5 TaMagiekunde +2', RSKo=2, ArBE=0.0, tint=LEAF,
      recipe=R('TaAlchimie', 7, [('Armor', 'hut_heilmagier', 1)], [(SILK, 1), (WART, 1)], [SAPHIRA], 6)),
    A('ww_shoes', 'amazing', 'schuhe_magier', 'Witchweave Slippers',
      'Soft shoes soled with silk and a warm firefly sac in each heel. You leave no prints worth following.',
      None, mods='AEmax +3 TaSchleichen +2', RSLB=1, RSRB=1, ArBE=0.0, tint=LEAF,
      recipe=R('TaAlchimie', 7, [('Armor', 'schuhe_magier', 1)], [(SILK, 1), (FSAC, 1)], [SAPHIRA], 6)),
    A('we_robe', 'legendary', 'oberteil_heilmagier', 'Emberweave Robe',
      'The Witchweave Robe threaded with glowing firefly silk and a green eye at the collar. Fire will not take it.',
      None, mods='AEmax +15 MR +2 TaPflanzenkunde +2', imm='fire', RSBr=3, RSRu=3, RSBa=3, RSLA=1, RSRA=1, ArBE=0.0, tint=EMBER,
      recipe=R('TaAlchimie', 12, [('Armor', 'arm_ww_robe', 1)], [(FSAC, 2), (SPIDER, 1)], [TALLON_MAGE], 14)),
    A('we_hood', 'superrare', 'hut_heilmagier', 'Emberweave Hat',
      'The Witchweave Hat with a glittering green eye set over the brim. It sees spells coming.',
      None, mods='AEmax +8 TaMagiekunde +3 IN +1', RSKo=2, ArBE=0.0, tint=EMBER,
      recipe=R('TaAlchimie', 11, [('Armor', 'arm_ww_hood', 1)], [(SPIDER, 1), (FSAC, 1)], [TALLON_MAGE], 10)),
    A('we_shoes', 'superrare', 'schuhe_magier', 'Emberweave Slippers',
      'Witchweave Slippers with ember-sac soles that never cool. Light steps, warm feet, quick hands.',
      None, mods='AEmax +5 TaSchleichen +2 GE +1', RSLB=1, RSRB=1, ArBE=0.0, tint=EMBER,
      recipe=R('TaAlchimie', 11, [('Armor', 'arm_ww_shoes', 1)], [(FSAC, 2)], [TALLON_MAGE], 10)),

    # ---- Hunter's leather, step 3 (Tallon): Skyhunter, harpy feathers over the Moonhowl pieces, plus a hood ----
    A('sh_mantle', 'legendary', 'schultern_nasreddin', 'Skyhunter Mantle',
      'The Moonhowl Mantle, fringed with harpy feathers. It catches the wind and turns arrows aside.',
      None, mods='TaWildnisleben +3 TaTierkunde +2 MR +2 AW +1', RSBr=2, RSRu=2, RSLA=3, RSRA=3, ArBE=0.2, tint=FROST,
      recipe=R('TaBogenbau', 13, [('Armor', 'arm_mh_mantle', 1)], [(HARPY, 3), (ISINEW, 1)], [TALLON_HUNTER], 14)),
    A('sh_grips', 'legendary', 'handschuhe_nasreddin', 'Skyhunter Grips',
      'The Moonhowl Grips with a bear claw over the draw finger and harpy down in the palm.',
      None, mods='TaBogen +3 TaRaufen +1 FF +2', RSLA=2, RSRA=2, ArBE=0.2, tint=SHADOW,
      recipe=R('TaBogenbau', 13, [('Armor', 'arm_mh_grips', 1)], [(HARPY, 2), (CLAW, 1)], [TALLON_HUNTER], 12)),
    A('sh_hood', 'superrare', 'helm_lederkappe', 'Skyhunter Hood',
      'A leather hood crested with harpy feathers. You see the hawk before the hawk sees you.',
      None, mods='TaSinnenschaerfe +3 TaBogen +1', RSKo=2, ArBE=0.2, tint=SHADOW,
      recipe=R('TaBogenbau', 11, [('Armor', 'helm_lederkappe', 1)], [(HARPY, 3), (STRIPS, 1)], [TALLON_HUNTER], 10)),
]
SETS_V24['tc_cuirass'] = (['arm_tc_cuirass', 'arm_tc_bracers', 'arm_tc_helm'], 'LEmax +2', 'TaSelbstbeherrschung +2 AUmax +5', 'Tuskhide')
SETS_V24['ts_cuirass'] = (['arm_ts_cuirass', 'arm_ts_bracers', 'arm_ts_helm'], 'LEmax +3', 'PA +1 MR +1', 'Ironshell')
SETS_V24['tw_cuirass'] = (['arm_tw_cuirass', 'arm_tw_bracers', 'arm_tw_helm'], 'LEmax +4', 'AT +1 PA +1', 'The Warlord')
SETS_V24['ww_robe'] = (['arm_ww_robe', 'arm_ww_hood', 'arm_ww_shoes'], 'AEmax +2', 'MR +1 IN +1', 'Witchweave')
SETS_V24['we_robe'] = (['arm_we_robe', 'arm_we_hood', 'arm_we_shoes'], 'AEmax +3', 'MR +2 KL +1', 'Emberweave')

# ---- arrows, step 2: Moon-sinew Arrows (Dark Forest village trader; the sinew only comes from the mad pack) ----
AMMO += [('am_moon_arrow', 'Pfeil', 'Moon-sinew Arrows', 'Fletched with a twist of moon-mad sinew. The shaft hums in flight, and sometimes sparks.',
          [('p', 100, [('dmg', 1, 0, 'physical', '')]), ('p', 15, [('dmg', 0, 1, 'magic', 'Lightning')])], 10,
          'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/1;Item/arm_tr_moon_sinew/1;', 9, DARK_TRADER, 7)]

# ---- beast parts instead of one shop ingredient: older plans need something hunted where they are sold ----
# (dragon-scale reforges keep their dragon materials; the new lines above already use beast parts)
BEAST_SWAP = {  # seller level prefix -> {shop material: (beast part, amount)}
    'location02': {GOLD: (TUSK, 2), GEMS: (CLAW, 1)},
    'location03': {GOLD: (WART, 2), GEMS: (CRAB, 2)}, 'location04': {GOLD: (WART, 2), GEMS: (CRAB, 2)},
    'location08': {GOLD: (FSAC, 2), GEMS: (LOUSE, 1)},   # scorpions only appear after Tallon (Murolosh mushroom garden)
    'location09': {GOLD: (LOUSE, 2), GEMS: (SPIDER, 1)},
}
SWAPPED = []
for _it in ITEMS:
    _r = _it['recipe']
    if (not _r or not _r['sellers'] or _it['key'][:3] in ('wp_', 'mh_', 'tc_', 'ts_', 'tw_', 'ww_', 'we_', 'sh_')
            or any(mid == SCALE for mid, _ in _r['mats'])):
        continue
    _sw = next((v for k, v in BEAST_SWAP.items() if _r['sellers'][0][1].startswith(k)), None)
    for _i, (mid, n) in enumerate(_r['mats']):
        if _sw and mid in _sw:
            _r['mats'][_i] = _sw[mid]; SWAPPED.append((_it['key'], mid, _sw[mid][0])); break

# =====================================================================================================================
# Armour rules (1 Nov): light / medium / heavy and early / mid / late / endgame, applied to every pack armour piece by build_armory.
# Class = material: Cloth = light (casters), Leather = medium-light, Metal = heavy. Caps = most total protection (sum of the 8 zones)
# a piece may have at its stage; floor = least encumbrance per point of protection. Both follow vanilla's own spread
# (e.g. leather cuirass 11 RS / 2.0 BE, dwarven plate 25 / 4.0, Iryan shoulders 8 / 0.2), so pack gear never out-armours vanilla
# for its stage. Stage = where the piece is first found or sold (chapter), else its tier.
# =====================================================================================================================
ARMOUR_SLOT = {'ChestArmor': 'chest', 'ChestArmorWithoutShoulder': 'chest', 'FullBodyArmor': 'chest', 'HeadArmor': 'head',
               'Shoulder': 'shoulder', 'ArmArmor': 'arms', 'GlovesWithArmArmor': 'arms', 'Gloves': 'gloves', 'LegArmor': 'legs',
               'Shoes': 'legs', 'ShoesWithLegArmor': 'legs', 'Trousers': 'legs', 'TrousersWithLegArmor': 'legs'}
ARMOUR_RULES = {  # (slot, material): ((early, mid, late, endgame) total RS cap, BE per RS point)
    ('chest', 'Cloth'): ((7, 9, 12, 14), 0.0), ('chest', 'Leather'): ((14, 17, 20, 23), 0.10), ('chest', 'Metal'): ((18, 22, 26, 30), 0.16),
    ('head', 'Cloth'): ((2, 3, 3, 4), 0.0), ('head', 'Leather'): ((4, 5, 6, 6), 0.10), ('head', 'Metal'): ((5, 6, 6, 7), 0.15),
    ('shoulder', 'Cloth'): ((3, 4, 5, 6), 0.0), ('shoulder', 'Leather'): ((6, 8, 10, 12), 0.025), ('shoulder', 'Metal'): ((8, 10, 12, 14), 0.05),
    ('arms', 'Leather'): ((6, 8, 10, 10), 0.03), ('arms', 'Metal'): ((8, 10, 12, 12), 0.04),
    ('gloves', 'Cloth'): ((2, 3, 4, 4), 0.0), ('gloves', 'Leather'): ((4, 6, 6, 8), 0.0), ('gloves', 'Metal'): ((6, 8, 10, 10), 0.03),
    ('legs', 'Cloth'): ((3, 4, 5, 6), 0.0), ('legs', 'Leather'): ((7, 9, 10, 12), 0.0), ('legs', 'Metal'): ((8, 10, 12, 14), 0.06),
}
TIER_STAGE = {'regular': 0, 'amazing': 0, 'superrare': 1, 'legendary': 2, 'mythic': 3}
def level_stage(lvl):
    import re as _re
    n = _re.search(r'(?:location|dungeon|loc|dun)_?(\d\d)', lvl or '')
    n = int(n.group(1)) if n else None
    return None if n is None else 0 if n <= 2 else 1 if n <= 5 else 2 if n <= 8 else 3
def item_stage(it):
    places = it['place'] if isinstance(it['place'], list) else ([it['place']] if it['place'] else [])
    lv = [level_stage(p[2] if p[0] != 'loot' else p[1]) for p in places] + [level_stage(l) for _, l in (it['recipe'] or {}).get('sellers', [])]
    lv = [x for x in lv if x is not None]
    return it['stage'] if 'stage' in it else min(lv) if lv else TIER_STAGE[it['tier']]
ZONES = ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')
GROUPS = (('RSKo',), ('RSBr',), ('RSRu',), ('RSBa',), ('RSLA', 'RSRA'), ('RSLB', 'RSRB'))
def armour_rules(base, over, stage):
    """Clamp a pack armour piece (base template row + its stat overrides) to the cap and encumbrance floor of its class and stage.
    Returns the changed columns (merged into over) and a note, or None when it already fits."""
    eq, mat = base['EquipmentType'], over.get('ArMaterial', base['ArMaterial'])
    rule = ARMOUR_RULES.get((ARMOUR_SLOT.get(eq), mat))
    if not rule: return None
    caps, floor = rule
    rs = {z: over.get(z, base[z]) or 0 for z in ZONES}
    total0 = total = sum(rs.values()); cap = caps[stage]
    while total > cap:
        g = max(GROUPS, key=lambda g: (rs[g[0]], len(g)))   # strongest zone first; a left/right pair drops together
        for z in g: rs[z] -= 1
        total = sum(rs.values())
    be0 = round(over.get('ArBE', base['ArBE']) or 0.0, 2)
    be = max(be0, -(-round(floor * total * 10, 6) // 1) / 10)
    if total == total0 and be == be0: return None
    over.update({z: v for z, v in rs.items() if v != (over.get(z, base[z]) or 0)}, ArBE=be)
    return f'RS {total0}->{total}, BE {be0}->{be}'

# pieces handed out in dialog have no shop to date them: Hagen's Moonhowl plans are chapter 2
for _it in ITEMS:
    if _it['key'] in ('mh_mantle', 'mh_jerkin', 'mh_breeches', 'mh_grips', 'mh_bow'): _it['stage'] = 1
    if _it['key'] == 'mw_jerkin': _it['stats']['ArMaterial'] = 'Leather'   # "elven leather" on a cloth-tagged base: medium, not a robe

# ---- plan bases that vanilla never sells or drops (found by tools/maint/obtainable.py): stock them where their plans are ----
# The Leather Cuirass and the Magician's Shoes only exist in a debug chest in the unmodded game.
BASE_STOCK += [('Armor', 'torso_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung', 'location02_grafenstadt'),
               ('Armor', 'torso_verstaerkte_lederruestung', 'Haendler_3_loc08_haendler_ruestung', 'location08'),
               ('Armor', 'schuhe_magier', 'Saphira_Trader', 'location03'),
               ('Armor', 'schuhe_magier', 'npc_magiertrainer_loc08_trainer_magie', 'location08')]

# ---- review 1 Nov (3) ----
# Saber of Embers: its plan is sold early in the Count's Town, but vanilla only sells the Khunchom Saber after Grimmzahn (harbour)
# and at the very end (Aldessia). One more at the Count's Town weapons dealer.
BASE_STOCK += [('Weapon', 'Khunchomer', 'staedter_reich_m_01_loc02_haendler_graf_waffen', 'location02_grafenstadt')]
# Heavy-duty Leather Pants (Darkwolf and Ranger's breeches): vanilla has one at Tallon and one in the Count's Town only after
# Grimmzahn. Two early at the Count's Town armourer, one more late there, one more in Tallon.
BASE_STOCK += [('Armor', 'hose_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung', 'location02_grafenstadt')] * 2 + [
               ('Armor', 'hose_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung_nachloc05', 'location02_grafenstadt'),
               ('Armor', 'hose_verstaerkte_lederruestung', 'Haendler_3_loc08_haendler_ruestung', 'location08')]
# Viper Fang sounded like Viper's Kiss
for _it in ITEMS:
    if _it['key'] == 'a_viper_fang': _it['name'] = "Serpent's Embrace"
# early plans whose base vanilla only offers from chapter 2 on (tools/maint/obtainable.py timing check): one early copy each
BASE_STOCK += [('Weapon', 'Partisane', 'staedter_reich_m_01_loc02_haendler_graf_waffen', 'location02_grafenstadt'),
               ('Armor', 'handschuhe_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung', 'location02_grafenstadt'),
               ('Armor', 'beine_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung', 'location02_grafenstadt'),
               ('Armor', 'helm_verstaerkte_lederruestung', 'Haendler_1_loc02_haendler_graf_ruestung', 'location02_grafenstadt')]
