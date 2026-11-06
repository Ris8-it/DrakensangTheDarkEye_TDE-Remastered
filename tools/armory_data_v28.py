# v2.8 the Thieves' Guild (2 Nov, docs/THIEVES_GUILD_PLAN.md). Exec'd last by armory_data.py.
# Everything here is sold or given by the guild members who join Cano's hall after each job (tools/build_secret_quests.py
# section 7), so nothing has a vanilla seller or a world place. Stages: 1 after the Dark Forest / Grimmzahn, 2 after Tallon,
# 3 after Murolosh. Black leather = Nasreddin's Iryan set; the glove line grows out of the vanilla Gloves of Shadow.
_TG = 'tg'
DARK_FANG, SPIDER_EYE, FIREFLY = 'arm_tr_wolf_fang', 'arm_tr_spider_eye', 'arm_tr_firefly_sac'
ITEMS_V28 = [
    # ---------------- job 1 (after the Dark Forest): Silke Quickfingers, the guild's fence ----------------
    W('tg_stiletto', 'amazing', 'Langdolch', 'Guild Stiletto', "A narrow guild blade with a cord-wrapped grip. It goes in between the rings of a mail shirt.",
      None, hit=[('p', 12, [('st', 'ArmBleeding')])], WpW6plus=4, WpATmod=1, value=D(30)),
    S('tg_buckler', 'amazing', 'Buckler', "Cutpurse's Buckler", 'A fist-sized buckler with a hidden pocket behind the boss.',
      None, mods='AW +1 TaTaschendiebstahl +1', WpPAmod=1, value=D(25)),
    W('tg_stars', 'amazing', 'Wurfsterne', 'Guild Throwing Stars', 'Blackened steel stars, balanced to fly flat and quiet.',
      None, hit=[('p', 15, [('st', 'ArmDazed')])], WpW6plus=2, stack=100, value=D(0.3)),
    A('tg_halfboots', 'amazing', 'schuhe_taschendieb', "Cutpurse's Half-Boots", 'Soft half-boots with felt soles. Cobbles, floorboards and gravel all keep quiet.',
      None, mods='TaSchleichen +2 TaTaschendiebstahl +1', RSLB=2, RSRB=2, value=D(18),
      recipe=R('TaBogenbau', 7, [('Armor', 'schuhe_taschendieb', 1)], [(STRIPS, 2)], [], 10)),
    A('tg_gloves1', 'amazing', 'handschuhe_des_diebes', 'Night Hand Gloves', 'The Gloves of Shadow, relined with wolf-fang grips by the guild. Locks and purses open for them.',
      None, mods='FF +3 TaTaschendiebstahl +2 TaSchloesser +1', RSLA=2, RSRA=2, value=D(55),
      recipe=R('TaBogenbau', 8, [('Armor', 'handschuhe_des_diebes', 1)], [(STRIPS, 2), (DARK_FANG, 1)], [], 12)),
    J('tg_phex_coin', 'amazing', 'Silberkette', "Phex's Lucky Coin", 'A worn coin with the fox of Phex on both sides. It always lands the right way up.',
      None, mods='TaSchloesser +2 TaFallenEntschaerfen +2 TaFeilschen +1', value=D(20)),

    # ---------------- job 2 (after Grimmzahn): Ravik Blackstitch, the guild's tailor ----------------
    A('tg_nr_veil', 'superrare', 'hut_turban_nasreddin', 'Nightrunner Veil', 'A black silk veil from the Iryan workshops. You see everything; nobody sees your face.',
      None, mods='TaSchleichen +2 TaSinnenschaerfe +2', RSKo=2, value=D(35),
      recipe=R('TaBogenbau', 9, [('Armor', 'hut_turban_nasreddin', 1)], [(STRIPS, 1), (GEMS, 1)], [], 14)),
    A('tg_nr_jerkin', 'superrare', 'torso_nasreddin', 'Nightrunner Jerkin', 'Black Iryan leather, cut close and oiled silent. No buckle catches the light.',
      None, mods='TaSchleichen +2 AW +1', RSBr=4, RSRu=3, RSBa=4, ArBE=1.1, value=D(60),
      recipe=R('TaBogenbau', 10, [('Armor', 'torso_nasreddin', 1)], [(STRIPS, 3), (SPIDER_EYE, 1)], [], 18)),
    A('tg_nr_boots', 'superrare', 'schuhe_nasreddin', 'Nightrunner Boots', 'Iryan boots with split soles. Roof tiles are no harder than a road.',
      None, mods='TaSchleichen +2 AW +1', RSLB=3, RSRB=3, value=D(40),
      recipe=R('TaBogenbau', 9, [('Armor', 'schuhe_nasreddin', 1)], [(STRIPS, 2)], [], 14)),
    A('tg_gloves2', 'superrare', 'handschuhe_des_diebes', 'Velvet Hand Gloves', 'The Night Hand, with a green spider-eye stitched into each palm. The fingers find the gap before the eye does.',
      None, mods='FF +3 AT +1 TaTaschendiebstahl +3 TaSchloesser +2', RSLA=3, RSRA=3, value=D(90),
      recipe=R('TaBogenbau', 11, [('Armor', 'arm_tg_gloves1', 1)], [(KOSH, 1), (SPIDER_EYE, 1)], [], 20)),
    W('tg_whisperthorn', 'superrare', 'Florett', 'Whisperthorn', 'A guild foil with a blade like a needle. Its owner never raised his voice, nor needed to.',
      None, hit=[('p', 10, [('st', 'ArmSundered')]), ('p', 10, [('buff', 'ArmQuickstep')])], WpW6plus=5, WpATmod=1, WpPAmod=0, value=D(80)),

    # ---------------- job 3 (after Tallon): Velane the Shade, blade master ----------------
    W('tg_velane_fang', 'superrare', 'Langdolch', "Velane's Fang", 'A long dirk with a groove for venom. The Silent Hand of Tallon paid in blood for the one they lost.',
      None, hit=[('p', 15, [('st', 'ArmVenom')]), ('p', 12, [('st', 'ArmBleeding')])], WpW6plus=6, WpATmod=1, value=D(120)),
    W('tg_shadow_stars', 'superrare', 'Wurfsterne', 'Shadow Stars', 'Black stars with serrated points, thrown three at a time by those who learned from Velane.',
      None, hit=[('p', 20, [('st', 'ArmBleeding')])], WpW6plus=4, stack=100, value=D(0.6)),
    A('tg_gloves3', 'legendary', 'handschuhe_des_diebes', 'Shadow Hand Gloves', 'The Velvet Hand, rubbed with a burnt firefly sac until it drinks the light. A blade in it never misses its moment.',
      None, mods='FF +3 AT +1 PA +1 AW +1 TaTaschendiebstahl +4 TaSchloesser +3', RSLA=3, RSRA=3, value=D(150),
      recipe=R('TaBogenbau', 13, [('Armor', 'arm_tg_gloves2', 1)], [(FIREFLY, 1), (GOLD, 1)], [], 30)),
    A('tg_fox_mask', 'legendary', 'hut_turban_nasreddin', 'Mask of the Fox', "A fox-faced half-mask in black silk. Guards remember a pleasant stranger and nothing else.",
      None, mods='CH +1 TaTaschendiebstahl +3 TaUeberreden +2 TaSchleichen +2', RSKo=2, value=D(110)),

    # ---------------- job 4 (after Murolosh): Old Fox Wendrik, the forger ----------------
    A('tg_gloves4', 'legendary', 'handschuhe_des_diebes', 'Hands of Phex', "The Shadow Hand, reforged by a dwarf who swore he never touched them. Phex himself would check his purse.",
      None, mods='FF +4 GE +1 AT +2 PA +1 AW +1 TaTaschendiebstahl +5 TaSchloesser +4', RSLA=4, RSRA=4, value=D(250),
      recipe=R('TaBogenbau', 15, [('Armor', 'arm_tg_gloves3', 1)], [(DWARF_STEEL, 1), (GEMS, 2)], [], 45, final=True)),
    A('tg_fox_boots', 'legendary', 'schuhe_nasreddin', 'Steps of the Fox', 'Iryan boots that a forger swears belonged to a saint. Nobody has ever heard them walk.',
      None, mods='GE +2 AW +2 TaSchleichen +4', RSLB=4, RSRB=4, value=D(180)),
    J('tg_phex_wink', 'legendary', 'Goldkette', "Phex's Wink", 'A gold fox with one emerald eye. Luck looks the other way for its enemies.',
      None, mods='FF +2 GE +1 AW +1 TaTaschendiebstahl +3 TaSchloesser +2', value=D(200)),
    W('tg_fortune', 'legendary', 'Rapier', "Fortune's Edge", 'A rapier with a coin set in the guard. It turns up heads more often than it should.',
      None, hit=[('p', 15, [('st', 'ArmSundered')]), ('if', 'ArmSundered', [('dmg', 0, 1, 'physical', '')]), ('p', 8, [('buff', 'ArmQuickstep')])],
      WpW6plus=8, WpATmod=2, WpPAmod=1, value=D(260)),
]
for _it in ITEMS_V28:
    k = _it['key']
    _it['stage'] = 1 if k in ('tg_stiletto', 'tg_buckler', 'tg_stars', 'tg_halfboots', 'tg_gloves1', 'tg_phex_coin', 'tg_nr_veil', 'tg_nr_jerkin',
                               'tg_nr_boots', 'tg_gloves2', 'tg_whisperthorn') else 2 if k in ('tg_velane_fang', 'tg_shadow_stars', 'tg_gloves3', 'tg_fox_mask') else 3
    _it['tint'] = _it['tint'] or SHADOW
ITEMS += ITEMS_V28
GUILD_STOCK = {   # guild member -> (type, key) sold; plans are 'Recipe', 'arm_rezept_<key>'
    'silke': [('Weapon', 'tg_stiletto'), ('Shield', 'tg_buckler'), ('Weapon', 'tg_stars'), ('Recipe', 'tg_halfboots'), ('Recipe', 'tg_gloves1'),
              ('Armor', 'schuhe_taschendieb'), ('Armor', 'handschuhe_des_diebes')],   # the glove line must not die if the vanilla pair was sold
    'ravik': [('Recipe', 'tg_nr_veil'), ('Recipe', 'tg_nr_jerkin'), ('Recipe', 'tg_nr_boots'), ('Recipe', 'tg_gloves2'), ('Armor', 'hut_turban_nasreddin'),
              ('Armor', 'torso_nasreddin'), ('Armor', 'schuhe_nasreddin'), ('Weapon', 'tg_stars')],
    'velane': [('Weapon', 'tg_velane_fang'), ('Weapon', 'tg_shadow_stars'), ('Recipe', 'tg_gloves3')],
    'wendrik': [('Armor', 'tg_fox_boots'), ('Weapon', 'tg_fortune'), ('Recipe', 'tg_gloves4')],
}
GUILD_REWARD = {1: 'tg_phex_coin', 2: 'tg_whisperthorn', 3: 'tg_fox_mask', 4: 'tg_phex_wink'}

# ---------------- Ronkwer, the bandit chief of the Blood Mountains (player, 2 Nov): he drops a heavy warrior's plate and a warhammer plan ----------------
ITEMS += [
    A('rk_plate', 'superrare', 'torso_kettenhemd_lang', "Ronkwer's Hauberk", "Ronkwer's long mail shirt, the rings doubled over chest and back and riveted by a smith who knew his trade. Lighter than it looks.",
      None, mods='LEmax +5', RSBr=5, RSRu=4, RSBa=5, RSLA=2, RSRA=2, RSLB=1, RSRB=1, ArBE=3.5, value=D(45)),   # player, 2 Nov: a better Long Shirt of Chain Mail, not plate
    W('rk_thunderhead', 'amazing', 'Kriegshammer', 'Thunderhead Warhammer', 'A war hammer rebalanced around a bear-claw spike. Easier to swing, harder to stop.',
      None, WpW6plus=4, WpATmod=1, WpPAmod=-1, value=D(45),   # player, 2 Nov: no knock-down; 2W6+4 (regular +2), AT +1 / PA -1
      recipe=R('TaSchmieden', 10, [('Weapon', 'Kriegshammer', 1)], [(STEEL, 2), ('arm_tr_bear_claw', 1)], [], 12)),
]
for _it in ITEMS[-2:]: _it['stage'] = 1; _it['tint'] = _it['tint'] or EARTH
LOOT_OWN[('NPC', 'Ronkwer')] = [('Armor', 'arm_rk_plate', 100, 1), ('Recipe', 'arm_rezept_rk_thunderhead', 100, 1)]

# ---------------- the Harpy Queen (Tallon, player, 2 Nov): her only drops besides her trophy are this plan and 20 feathers ----------------
ITEMS += [
    A('hq_crest', 'superrare', 'helm_verstaerkte_lederruestung', "Harpy Queen's Crest", "A leather hood crowned with the Harpy Queen's long storm-grey feathers. "
      "The wind tells you where an arrow should go.", None, mods='FK +2 TaSinnenschaerfe +2 AW +1', RSKo=4, value=D(70),
      recipe=R('TaBogenbau', 12, [('Armor', 'helm_verstaerkte_lederruestung', 1)], [('zutat_b_harpyienfedern', 6), (GOLD, 1)], [], 18)),
]
ITEMS[-1]['stage'] = 2; ITEMS[-1]['tint'] = THUNDER

# ---------------- Duskarrow (player, 3 Nov): a longbow now, and its song ----------------
_DUSK = ("Faelwen's bow, cut from a yew that grew where the moon touches the water. It was strung to sing to the forest, and he taught it to "
         "hunt the forest's own children. Gwendala hears it still: a thin, grieving note beneath the string, the song of a bow that hated "
         "every arrow it was made to loose. Hold it gently. It is listening for a kinder hand.")
_REDEEMED = ("In Gwendala's hands the grieving note is gone. She sang to it for a night and a day, the old songs of her people, and the bow "
             "learned them one by one: the song of the hunt that feeds the camp, the song of the watch at the forest's edge, the song of "
             "the long way home. It will learn more. An elven bow has time.")
_set('l_duskarrow', base='Langbogen', flavor=_DUSK, stats=dict(WpW6=1, WpW6plus=7))   # 1D6+8 after its folded hit (player: 2D6 too wild for chapter 2)
_set('m_rf_duskarrow', base='Langbogen', flavor=_REDEEMED, stats=dict(WpW6=2))      # the endgame reforge keeps 2D6
# the Harpy Queen's Crest: there is no ranged-damage stat for gear (Hawkeye is a spell state), so it aims better instead of seeing more
for _it in ITEMS:
    if _it['key'] == 'hq_crest': _it['mods'] = 'FK +3 AW +1'
# ---------------- Duskfeather Arrows (player, 3 Nov): Faelwen's own, a unique reward; a little magic that armour does not stop ----------------
AMMO.append(('am_duskfeather', 'Pfeil', 'Duskfeather Arrows', "Faelwen's arrows, fletched with dusk-grey feathers and bound with moon-mad sinew. "
             "They whisper on the string, and no mail has ever kept the whisper out.", [('p', 100, [('dmg', 2, 0, 'magic', 'Kulminatio_Impact')])], 10,
             'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/1;Item/arm_tr_moon_sinew/1;', 10, (None, None), 10))

