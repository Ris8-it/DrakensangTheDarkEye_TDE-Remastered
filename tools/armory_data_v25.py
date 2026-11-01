# ======================= v2.5: balance audit pass (docs/reviews/2026-10-30/BALANCE_AUDIT.md) =======================
# Executed last inside armory_data.py. Overrides existing item entries by key; one line per decision, with the audit id.
# Budgets: reforges stay >= 1 average damage below the matching Pal'Na'Thar weapon (they win on effects, not raw numbers);
# Forgrimm <= +6 Strength from pack items at endgame (+2 by Tallon); Rhulana <= AT +5 / PA +4; no attributes/regeneration before Moorbridge;
# fire immunity from Tallon on; nothing craftable from an ordinary base is also placed as loot.
_IT = {it['key']: it for it in ITEMS}
def _p(key, **kw):
    it = _IT[key]
    st = kw.pop('stats', None)
    if st is not None:
        for k, v in st.items():
            if v is None: it['stats'].pop(k, None)
            else: it['stats'][k] = v
    if 'flavor_add' in kw: it['flavor'] = it['flavor'].rstrip('.') + '. ' + kw.pop('flavor_add')
    it.update(kw)

# ---- A2: final-weapon hierarchy (below the Pal'Na'Thar weapons in raw damage) ----
_p('m_rf_lion_queen', stats=dict(WpW6plus=11, WpATmod=2))
_p('m_rf_rondra_verdict', stats=dict(WpW6plus=10, WpATmod=2))
_p('m_rf_last_oath', stats=dict(WpW6plus=9, WpATmod=1))          # keeps the Dragonslayer 14/1 Strength scaling (base weapon unchanged)
_p('m_rf_exile', stats=dict(WpW6plus=9))
_p('m_rf_sala', stats=dict(WpW6plus=4), hit=[h for h in _IT['m_rf_sala']['hit'] if h != ('p', 15, [('st', 'stun')])])   # B13: one stun, not two
_p('m_rf_duskarrow', stats=dict(WpW6plus=5))
_p('m_rf_crimson', stats=dict(WpW6plus=9, WpATmod=2))
_p('m_rf_phex', stats=dict(WpW6plus=8, WpATmod=2))
# ---- A3: Japhgur hoard vs Wyrm crafting ----
_p('l_fang_lioness', mods='MU +1', stats=dict(WpW6plus=8, WpATmod=1))
_p('w_scale_cuirass', stats=dict(RSBr=8, RSRu=7, RSBa=8, RSLA=3, RSRA=3, RSLB=2, RSRB=2, ArBE=3.5))   # the best metal torso
_p('fx_plate', stats=dict(RSBr=7, RSRu=6, RSBa=7, RSLA=2, RSRA=2, RSLB=2, RSRB=2, ArBE=3.5))
_p('w_hide_jerkin', stats=dict(ArBE=1.5))
_p('w_scale_shield', stats=dict(WpATmod=-1, WpPAmod=3))
# ---- A4: Forgrimm Strength budget ----
_p('h_fo3', mods='KK +1 KO +1 LEmax +5 TaSchmieden +3')
_p('h_fo4', mods='KK +2 KO +2 LEmax +10')
_p('j_mountain_king', mods='KK +1 KO +2')
_p('j_red_rage', mods='AT +3 PA -3 MR -2', place=(C, 'loc10_chest_zwergenskelett', 'location10'))   # A9: cursed ring, deep place
_p('fx_gauntlets', mods='AT +1')
_p('a_ox_ring', mods='KO +1 LEmax +5', place=(L, 'loot_loc09_kiste_aldessia2', 'all'))            # A9
# ---- A5: Rhulana AT/PA budget ----
_p('h_rh4', mods='MU +3 AT +1 PA +1 LEmax +10 TaSaebel +2')
_p('j_crimson_circle', mods='AT +1 PA +1 GE +1 MU +1')
_p('j_amazon_queen', mods='MU +2 GE +1')
SETS_V24['h_rh3'] = (_RH, 'LEmax +4', 'LEmax +5 MU +1', 'Regalia of the Lion Queen')
SETS_V24['h_rh4'] = (_RH, 'LEmax +5', 'LEmax +10 MU +1 GE +1', 'Regalia of the Lion Queen')
SETS_V24['h_fo4'] = (_FO, 'LEmax +5', 'AT +1 KO +1 LEmax +10', "Ferolax's Forge-Panoply")
# ---- A8: weapon-chain endpoints and craftable items are never also placed ----
for _k in ('d_black_widow', 's_rondra_reprimand', 's_mountain_patience', 's_nightsong', 'a_ironfist', 'a_ranger_breeches', 'a_bloodletter', 'a_thunder_shortsword'):
    _p(_k, place=None)
_p('w_whisperwind', place=(C, 'loc08_gruft_sarg_tagebuch_05', 'dungeon08_gruft_01'))
# ---- A9: Tallon over-density ----
_p('a_clear_mind', place=(C, 'skelett_tot_sitzend_loc05', 'dungeon05_burg'))
_p('j_bulwark', place=(L, 'loot_loc09_kiste_aldessia3', 'all'))
_p('j_spellblade', place=(L, 'loot_loc10_geheimraum_01', 'all'))
# ---- A10: one set piece per set into Gruldur (rewards earlier than the Fire Falls) ----
_p('fx_boots', place=(L, 'loot_loc10_teleportertruhe', 'all'))
_p('mw_treads', place=(L, 'loot_loc10_geheimraum_03', 'all'))
_p('gt_boots', place=(C, 'loc10_chest_zwergenskelett', 'location10'))
_p('m_last_oath', place=(C, 'loc10_chest_zwergenskelett', 'location10'))     # reforgeable in Murolosh without a return trip from the Falls
# ---- A11: the codex reward is a robe the Arcane Thief wears (the staff stays out of the game) ----
ITEMS.append(A('m_rk_robe', 'legendary', 'oberteil_magierrobe_schwarz', "Rakorium's Robe of Disputation",
               'Rakorium won every academic argument in this robe, mostly by talking until the other side left. It is warm, and smells of ink.',
               None, mods='AEmax +10 MR +2 KL +1', RSBr=2, RSRu=2, RSBa=2, RSLA=1, RSRA=1, tint=ASTRAL))
# ---- B1: Moorbridge skeleton jackpot ----
_p('g_salamander_robe', place=(C, 'hesperia_schuttberg', 'dungeon08_haendler'))
_p('a_longshot_bracers', mods='FF +1')
# ---- B2: duelist weapons that come early ----
_p('s_riposte', mods='', stats=dict(WpPAmod=1))
_p('l_duskarrow', tier='superrare', mods='FF +1', stats=dict(WpW6plus=2))
# ---- B3/B4/B5: Rhulana's heavy pieces ----
_p('lq_helm', mods='PA +1', stats=dict(RSKo=4))
_p('lq_cuirass', stats=dict(RSBr=6, RSRu=6, RSBa=6, ArBE=2.5))
_p('k_warboots', stats=dict(RSLB=6, RSRB=6))
# ---- B6: early attribute leaks ----
_p('j_emberheart', mods='LEmax +5 TaSelbstbeherrschung +2', imm='')
_p('j_serpent', mods='FF +1')
_p('j_gambler', mods='CH +3 TaFeilschen +5 MU -1', tier='legendary', place=('loot', 'loot_loc08_bestie_truhe_leiche_02', 'all'),
   flavor='An ivory die set in silver, still clutched by a gambler the Night Beast caught. Phex smiles; your courage wavers.')   # review 1 Nov: far too strong for the Ferdok thieves' guild; now Tallon, on the dice-player's corpse in the beast's lair
_p('j_rk_spectacles', mods='KL +1 IN +1 MR +1 TaMagiekunde +3')
_p('a_klingenhand_gloves', mods='AT +1 PA +1')
_p('s_archon_rod', place=(L, 'loot_loc05_truhe_drachenraum_04', 'all'))
# ---- B8: immunity glut (knockdown/fire immunity later) ----
_p('a_rondra_ward', mods='MR +1', imm='')
_p('a_unbowed', mods='AUmax +5', imm='')
_p('s_ashblade', imm='')
_p('a_kosch_ember_axe', imm='')
# ---- B9: Nightfox = stealth and locks set, the Stolen Grimoire = caster set ----
_p('n_gloves', mods='FF +2 TaSchloesser +3')
_p('n_breeches', mods='MR +1 TaTaschendiebstahl +2 TaSchleichen +2')
_p('n_jerkin', mods='GE +2 AW +1 TaSchleichen +2')
_p('s_thinking_cap', mods='AEmax +15 MR +2 KL +1')
SETS_V24['h_th4'] = (_TH, 'AEmax +3', 'GE +1 AW +2 AT +1', 'The Stolen Grimoire')
# ---- B10: one Forgrimm breastplate (Ferolax's) ----
_p('l_forgefather_plate', place=None)
# ---- B11: Heart of Umbracor becomes a ring and stops crowding out the amulet heirlooms ----
_p('l_heart_umbracor', base='Goldring', mods='MU +1 KL +1 IN +1 CH +1 LEmax +10 AEmax +10')
# ---- B12: bows ----
_p('a_hawkstring', place=None)
_p('a_moonbow', stats=dict(WpW6plus=4), value=D(20))
# ---- B16: ammunition wounds ----
AMMO[:] = [(a[0], a[1], a[2], a[3], [('p', 6, [('st', 'wound')])], *a[5:]) if a[0] in ('am_barbed_arrow', 'am_barbed_bolt') else a for a in AMMO]
# ---- C5: heirloom stage numbers in the name ----
for _k in [k for k in _IT if k.startswith('h_')]:
    _IT[_k]['name'] += ' (' + ['I', 'II', 'III', 'IV'][int(_k[-1]) - 1] + ')'
# ---- A1: Elf wood finally has a source (Gwendala's heirloom, bow reforges and the Nightsong chain need it) ----
ELFWOOD_STOCK = [(L, 'loot_loc04_skelett_sitzend', 5),   # 5: the ghost's skeleton, looted after the fight, when Gwendala joins
                 (L, 'loot_loc04_truhe_2', 2), ('npc', 'npc_elfentrainer', 'location02_praios', 2),
                 ('npc', 'Jaeger_Kauzenstein_loc08_jaeger', 'location08', 2), ('npc', 'Zwerg_Handwerker_loc09_zutatenhaendler', 'location09', 2)]

# ======================= round 2 (31 Oct): the audit's remaining items =======================
# ---- B7: Spellthief's Dirk only from Wagnitz in the Blood Mountains (own loot table, built in build_armory), AE-on-hit 15% ----
_p('a_spellthief_dirk', place=None, hit=[('p', 15, [('asp', 1)]), ('p', 12, [('st', 'ArmHexed')])])
WAGNITZ_DROP = ('wagnitz_drachenkultist_loc03', 'loot_unique_wagnitz_drachenkultist_loc03', 'arm_a_spellthief_dirk')
# ---- N10: the Thinking Cap stops copying Rakorium's Best Hat ----
_p('s_thinking_cap', mods='AEmax +10 IN +1 KL +1')
# ---- N4: shoulders for the slots nobody filled ----
ITEMS += [
    A('lq_pauldrons', 'superrare', 'schultern_plattenruestung_01', 'Lioness Pauldrons', 'Gilded shoulder plates with lion heads. Sabeth wore them over the stolen cuirass.',
      None, mods='MU +1 LEmax +5', RSBr=2, RSRu=2, RSLA=3, RSRA=3, ArBE=0.5, tint=HOLY),
    A('mw_mantle', 'superrare', 'schultern_nasreddin', "Moonwarden's Mantle", 'A short grey-green shoulder cape of Iryan leather. It whispers when an arrow is about to be loosed.',
      (C, 'hesperia_schuttberg', 'dungeon08_haendler'), mods='IN +1 TaSinnenschaerfe +2', RSBr=1, RSRu=1, RSLA=2, RSRA=2, tint=LEAF),
    A('a_patch_mantle', 'amazing', 'schultern_verstaerkte_lederruestung', "Thief's Patch-Mantle", 'Stitched from a dozen stolen cloaks. Each patch remembers a different alley.',
      (N, 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde'), mods='TaSchleichen +2 AEmax +5', RSLA=1, RSRA=1, value=D(30), tint=SHADOW),
# ---- N3: Forgrimm's chapter 2-3 two-hander (given by the Blood Mountains woodcutter, secret_quests) ----
    W('r_splitting_maul', 'regular', 'Kriegshammer', "Holdwin's Splitting Maul", 'The woodcutter swore by it for thirty years. Logs, bandits, the occasional stubborn bear.',
      None, hit=[('p', 8, [('st', 'overthrown')])], WpW6=2, WpW6plus=2, WpTPKK1=13, WpTPKK2=2, value=D(9)),
]
DUELIST_PIECES['sabeth'] = ['arm_lq_cuirass', 'arm_lq_pauldrons']
# ---- N2: Pal'Na'Thar tempers the Fire weapon you chose (one Heavy Wyrm Scale; recipe handed over in his dialogue) ----
TEMPERED = [  # base fire weapon, new key, name, extra proc, recipe skill
    ('weapon_unique_zyklopen_saebel', 'tp_firesong', 'Firesong, Tempered', ('p', 10, [('buff', 'ArmLionroar')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_schwert', 'tp_flamesong', 'Flamesong, Tempered', ('p', 10, [('buff', 'ArmTrance')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_axt', 'tp_firestrike', 'Firestrike, Tempered', ('p', 12, [('st', 'ArmSundered')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_zweihandschwert', 'tp_flamestrike', 'Flamestrike, Tempered', ('p', 10, [('st', 'ArmShaken')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_zweihandaxt', 'tp_flamefury', 'Flamefury, Tempered', ('p', 10, [('buff', 'ArmIronskin')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_speer', 'tp_firespike', 'Firespike, Tempered', ('p', 12, [('st', 'ArmBleeding')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_schwererdolch', 'tp_firethorn', 'Firethorn, Tempered', ('p', 10, [('buff', 'ArmShadowstep')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_rapier', 'tp_sparksting', 'Sparksting, Tempered', ('p', 10, [('buff', 'ArmQuickstep')]), 'TaSchmieden'),
    ('weapon_unique_zyklopen_stab', 'tp_sparkstrike', 'Sparkstrike, Tempered', ('p', 12, [('st', 'ArmStarburn')]), 'TaBogenbau'),
    ('weapon_unique_zyklopen_bogen', 'tp_firestorm', 'Firestorm, Tempered', ('p', 12, [('st', 'ArmDazed')]), 'TaBogenbau'),
    ('weapon_unique_zyklopen_armbrust', 'tp_flamesting', 'Flamesting, Tempered', ('p', 12, [('st', 'ArmBleeding')]), 'TaBogenbau'),
]

# ---- final check (1 Nov): crafted-only rule for the dwarven pauldrons; drop the cut items entirely ----
_p('d_pauldrons', place=None)
ITEMS[:] = [it for it in ITEMS if it['key'] not in ('a_hawkstring', 'l_forgefather_plate', 'm_rk_staff', 'r_skinner')]   # r_skinner is a quick-slot tool in remastered_systems now

# ---- review 1 Nov: Owlstone's cap uses the game's real Hunter's Cap (model and icon) under its own name ----
_p('r_hunters_cap', base='hut_jaeger', name="Owlstone's Hunting Cap")   # hunter's cap model, our own icon

# ---- review 1 Nov: the Wolfpack, a light leather line from wolf trophies (Bowyer) ----
# White Fur drops a Silver Ruff (its quest pelt stays for Owlstone): the mantle, craftable in Ferdok. Dark Wolf Pelts come from skinning the
# big wolves of the wilds later (skin_wolf_mittel / skin_wolf_groß, added in build_remastered.py): jerkin, breeches, grips. Iryan-leather models.
RUFF, DARKPELT, WFANG = 'arm_tr_silver_ruff', 'arm_tr_darkwolf_pelt', 'arm_tr_wolf_fang'
MATERIALS += [
    ('tr_silver_ruff', 'Wolfsfell', 'Silver Ruff of White Fur', "The thick silver-white ruff from White Fur's neck. Too fine for a trophy wall; a bowyer could work it into something you wear.", 1500, []),
    ('tr_darkwolf_pelt', 'Wolfsfell', 'Dark Wolf Pelt', 'A near-black pelt from one of the big wolves of the wild country. Supple, warm and quiet as a shadow.', 600, []),
]
ITEMS += [
    A('wp_mantle', 'amazing', 'schultern_nasreddin', 'White Fur Mantle', "Iryan leather shoulders lined with White Fur's silver ruff. The other wolves smell their old leader on you, and hesitate.",
      None, mods='TaWildnisleben +2 TaTierkunde +1', RSBr=1, RSRu=1, RSLA=2, RSRA=2, ArBE=0.2, tint=FROST,
      recipe=R('TaBogenbau', 6, [], [(RUFF, 1), ('Wolfsfell', 2), (STRIPS, 2)], [FERDOK_BOWYER, TALLON_HUNTER], 6)),
    A('wp_jerkin', 'superrare', 'torso_nasreddin', 'Darkwolf Jerkin', 'Iryan leather faced with dark wolf pelt. Light enough to run in, quiet enough to hunt in.',
      None, mods='TaSchleichen +2 AUmax +5', RSBr=3, RSRu=3, RSBa=3, RSLA=1, RSRA=1, ArBE=1.0, tint=SHADOW,
      recipe=R('TaBogenbau', 10, [], [(DARKPELT, 3), (STRIPS, 2), (ISINEW, 1)], [FERDOK_BOWYER, TALLON_HUNTER], 10)),
    A('wp_breeches', 'superrare', 'hose_verstaerkte_lederruestung', 'Darkwolf Breeches', 'Heavy-duty leather trousers, reworked with dark wolf pelt at the knees and belt. They no longer creak.',
      None, mods='TaSinnenschaerfe +2', RSBa=1, RSLB=3, RSRB=3, ArBE=0.0, tint=SHADOW,
      recipe=R('TaBogenbau', 9, [('Armor', 'hose_verstaerkte_lederruestung', 1)], [(DARKPELT, 2), (STRIPS, 1)], [FERDOK_BOWYER, TALLON_HUNTER], 8)),
    A('wp_grips', 'amazing', 'handschuhe_nasreddin', 'Darkwolf Grips', 'Iryan leather gloves with two wolf fangs set over the knuckles. A steady bow hand, and a nasty fist.',
      None, mods='TaBogen +1 TaRaufen +1', RSLA=2, RSRA=2, ArBE=0.2, tint=SHADOW,
      recipe=R('TaBogenbau', 8, [], [(DARKPELT, 1), (WFANG, 2), (STRIPS, 1)], [FERDOK_BOWYER, TALLON_HUNTER], 7)),
]
_WP = ['arm_wp_mantle', 'arm_wp_jerkin', 'arm_wp_breeches', 'arm_wp_grips']
SETS_V24['wp_jerkin'] = (_WP, 'AUmax +2', 'AW +1 TaSchleichen +2', 'The Wolfpack')

# ---- review 1 Nov (2): every wolf plan is sold by Crooked Otto in the Count's Town, not on arrival in Ferdok ----
OTTO = ('holzfaeller_loc02_haendler_graf_fliegender', 'location02_grafenstadt')
for _it in ITEMS:
    if _it['key'] in ('wp_mantle', 'wp_jerkin', 'wp_breeches', 'wp_grips'): _it['recipe']['sellers'] = [OTTO]

# ---- the Moonhowl tier: Alvina's moon-mad pack in the Dark Forest (secret_quests: "The Mad Pack") ----
# Its materials exist only on that pack. Hagen the goatherd hands over the four Moonhowl plans and the bow plan when the pack is dead
# (no seller: nothing shows up in a shop before then). The Iryan shoulder upgrade is sold later, by the Tallon hunter.
MPELT, MSINEW, MANE, HEART = 'arm_tr_moonmad_pelt', 'arm_tr_moon_sinew', 'arm_tr_greymaw_mane', 'arm_tr_storm_heart'
MATERIALS += [
    ('tr_moonmad_pelt', 'Wolfsfell', 'Moon-mad Pelt', 'A grey wolf pelt shot through with silver where the madness took hold. It bristles when anyone nearby casts a spell.', 900, []),
    ('tr_moon_sinew', 'zutat_b_verbesserte_sehne', 'Moon-mad Sinew', 'Sinew from a moon-mad wolf. It hums when drawn tight, like a bowstring that wants to be plucked.', 400, []),
    ('tr_greymaw_mane', 'Wolfsfell', "Greymaw's Mane", "The iron-grey mane of the mad alpha. Even cut loose, it stands on end.", 2500, []),
    ('tr_storm_heart', 'zutat_s_edelsteine', "Stormhowl's Heartstone", 'A pale stone from the white wolf that ran with the pack. Sparks crawl over it when you close your hand.', 3000, []),
]
ITEMS += [
    A('mh_mantle', 'superrare', 'schultern_nasreddin', 'Moonhowl Mantle', "The White Fur Mantle, re-lined with moon-mad pelt. Spells seem to lose their way before they reach you.",
      None, mods='TaWildnisleben +3 TaTierkunde +2 MR +1', RSBr=1, RSRu=1, RSLA=3, RSRA=3, ArBE=0.2, tint=FROST,
      recipe=R('TaBogenbau', 10, [('Armor', 'arm_wp_mantle', 1)], [(MPELT, 2), (MSINEW, 1), (STRIPS, 2)], [], 10)),
    A('mh_jerkin', 'legendary', 'torso_nasreddin', 'Moonhowl Jerkin', "The Darkwolf Jerkin, rebuilt around Greymaw's mane. Light as ever, and nothing in the woods hears you coming.",
      None, mods='TaSchleichen +3 AUmax +10 GE +1', RSBr=4, RSRu=4, RSBa=4, RSLA=1, RSRA=1, ArBE=1.0, tint=SHADOW,
      recipe=R('TaBogenbau', 13, [('Armor', 'arm_wp_jerkin', 1)], [(MANE, 1), (MPELT, 2), (MSINEW, 1)], [], 14)),
    A('mh_breeches', 'superrare', 'hose_verstaerkte_lederruestung', 'Moonhowl Breeches', 'The Darkwolf Breeches with moon-mad pelt over the thighs. You hear the twig before you step on it.',
      None, mods='TaSinnenschaerfe +3 AUmax +5', RSBa=1, RSLB=4, RSRB=4, ArBE=0.0, tint=SHADOW,
      recipe=R('TaBogenbau', 11, [('Armor', 'arm_wp_breeches', 1)], [(MPELT, 2), (STRIPS, 1)], [], 10)),
    A('mh_grips', 'superrare', 'handschuhe_nasreddin', 'Moonhowl Grips', 'The Darkwolf Grips, re-stitched with humming sinew. The bow hand never shakes.',
      None, mods='TaBogen +2 TaRaufen +1 FF +1', RSLA=2, RSRA=2, ArBE=0.2, tint=SHADOW,
      recipe=R('TaBogenbau', 11, [('Armor', 'arm_wp_grips', 1)], [(MPELT, 1), (MSINEW, 2)], [], 10)),
    W('mh_bow', 'legendary', 'Langbogen', 'Moonhowl Longbow', 'A longbow strung with moon-mad sinew. When it looses, the string howls, and sometimes lightning answers.',
      None, hit=[('p', 100, [('dmg', 1, 0, 'physical', '')]), ('p', 20, [('dmg', 0, 1, 'magic', 'Lightning')])], WpATmod=1, tint=THUNDER,
      recipe=R('TaBogenbau', 12, [('Weapon', 'Langbogen', 1)], [(MSINEW, 3), ('zutat_b_elfenholz', 1)], [], 12)),
    A('mh_iryan_shoulders', 'legendary', 'schultern_nasreddin', 'Stormhowl Shoulder Guards',
      "Iryan leather shoulder guards with Stormhowl's heartstone sewn under the left plate. Lightning-quick, and spells slide off them.",
      None, mods='MR +2 AW +1 TaSinnenschaerfe +2', RSBr=2, RSRu=2, RSLA=4, RSRA=4, ArBE=0.2, tint=THUNDER,
      recipe=R('TaBogenbau', 12, [('Armor', 'schultern_nasreddin', 1)], [(HEART, 1), (MPELT, 2), (STRIPS, 2)], [TALLON_HUNTER], 14, final=True)),
]
_MH = ['arm_mh_mantle', 'arm_mh_jerkin', 'arm_mh_breeches', 'arm_mh_grips']
SETS_V24['mh_jerkin'] = (_MH, 'AUmax +3', 'AW +1 TaSchleichen +3 MR +1', 'The Moonhowl Pack')

# ---- review 1 Nov (2): Kosh-steel Arrows are now hunters' arrows built from animal loot (no Kosh steel) ----
AMMO[:] = [(a[0], a[1], "Kosch Hunter's Arrows", 'Kosch hunters grind boar tusk and wolf fang into heads harder than iron and bind them with sinew. '
            'They punch through leather and mail.', a[4], a[5],
            'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/arm_tr_boar_tusk/1;Item/arm_tr_wolf_fang/1;Item/zutat_b_sehnen/1;Item/zutat_b_gaensefedern/1;',
            *a[7:]) if a[0] == 'am_kosh_arrow' else a for a in AMMO]

# ---- review 1 Nov (2): Whisper of Phex is far too strong for the Ferdok thieves' guild: the seated skeleton in Castle Grimmzahn instead ----
_p('s_phex_whisper', place=('chest', 'skelett_tot_sitzend_loc05', 'dungeon05_burg'))
