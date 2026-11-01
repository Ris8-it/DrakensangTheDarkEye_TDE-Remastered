"""Armory v2 item data (playtest revision, 30 October 2026). Read by build_armory.py.

Review rules applied (docs/reviews/2026-10-30): weapons/armour/shields use ONLY native permanent effects
(tooltip-safe, composed by the generator from `mods`/`imm`); jewelry may use custom effects and auras.
No Marked Prey. Early jewelry = talents/social. Wounds limited early, regeneration late. Forgrimm = two-handed.
Never elven/buckskin boots. Mythicals are dungeon finds only.

DSL (dsa.py): ('p', pct, [...]) chance · ('if', status, [...]) vs target status
  actions: ('st', id) · ('dmg', fixed, dice_n, type, fx) · ('heal', n) · ('asp', n) · ('buff', se)
Placement: ('chest'|'npc', Id, level) explicit storage · ('loot', table, mode).
Recipe: dict(skill, diff, consumes=[(Type, Id, n)], mats=[(Id, n)], sellers=[(npc, level)], price=D, final=bool)
"""
D = lambda d: int(d * 100)   # ducats -> heller

HURT = lambda f, d, n, t: f'Hurt fixedDamage="{f}" dice="{d}" diceAmount="{n}" showNoDamage="false" damageType="{t}" actionSelection="script,quest,dialog"; '
WAIT = lambda s: f'WaitAction duration="{s}" permanent="false" actionSelection="script"; '
HEAL = lambda n: f'Heal fixedLE="{n}" dice="6" diceAmount="0" actionSelection="script,quest,dialog"; '
ASP = lambda n: f'RestoreAsP fixedAsP="{n}" dice="6" diceAmount="0" actionSelection="script"; '
BAD = 'modifier;debuff;bad'
STATUS = [  # id, name, description, start mods, duration, ticks, state effect, hardpoint, icon, categories, immunity
    ('ArmSundered', 'Sundered Guard', 'Guard broken: Parry -3, Dodge -2.', 'PA -3 AW -2', 10, None, 'Plumbarum_State', 'Damage_Torso', 'status_fx_bad_fracture', BAD, ''),
    ('ArmShaken', 'Shaken', 'Nerve broken: Courage -3, Attack -2.', 'MU -3 AT -2', 10, None, 'Horriphobus_State', 'Head', 'status_fx_spell_horriphobus', BAD + ';noEffectOnUndead', ''),
    ('ArmBleeding', 'Bleeding', 'Loses 1d3+1 LE every 2 seconds, four times.', '', 0, [HURT(1, 3, 1, 'physical'), WAIT(2)] * 4, '', '', 'status_fx_verwundet', 'bad;dot;wound;noEffectOnUndead', ''),
    ('ArmHexed', 'Hexed', 'Magic resistance -4, Cleverness -2.', 'MR -4 KL -2', 15, None, 'Sanftmut_State', 'Damage_Torso', 'status_fx_bad_minus', BAD + ';magic', ''),
    ('ArmDazed', 'Dazed', 'Reeling: Attack -3, Ranged combat -3.', 'AT -3 FK -3', 6, None, '', '', 'status_fx_bad_flash', BAD, ''),
    ('ArmVenom', 'Wyrm Venom', 'Strength -2 and 1d6+2 poison damage every 3 seconds, three times.', 'KK -2', 0, [HURT(2, 6, 1, 'poison'), WAIT(3)] * 3, '', '', 'status_fx_wunde_vergiftet', 'poison;hardPoison;bad;noEffectOnUndead', ''),
    ('ArmTrance', 'Battle Trance', 'Attack +2, Parry +1.', 'AT +2 PA +1', 10, None, 'Kampf_Offensiv1', 'Head', 'status_fx_spell_kampfrausch', 'buff;good', ''),
    ('ArmLionroar', "Lion's Roar", 'Courage +3, Attack +2, Parry +2.', 'MU +3 AT +2 PA +2', 12, None, 'AttributoMU_State', 'Skeleton_Root', 'status_fx_spell_attributo_mu', 'buff;good', ''),
    ('ArmIronskin', 'Iron Skin', 'Parry +2, Dodge +2, Magic resistance +2.', 'PA +2 AW +2 MR +2', 10, None, 'Armatrutz_State', 'Damage_Torso', 'status_fx_spell_armatrutz', 'buff;good', ''),
    ('ArmSecondwind', 'Second Wind', 'Regains 2 LE every 2 seconds, four times.', '', 0, [HEAL(2), WAIT(2)] * 4, 'Balsam_State', 'Skeleton_Root', 'status_fx_regenerierend', 'buff;good', ''),
    ('ArmAstralsurge', 'Astral Surge', 'Regains 3 AE every 2 seconds, three times.', '', 0, [ASP(3), WAIT(2)] * 3, 'AttributoKL_State', 'Skeleton_Root', 'status_fx_spell_attributo_kl', 'buff;good', ''),
    ('ArmQuickstep', 'Quickstep', 'Agility +2, Dodge +2, Attack +1.', 'GE +2 AW +2 AT +1', 10, None, 'Axxeleratus_State', 'Skeleton_Root', 'status_fx_spell_axxeleratus', 'buff;good', ''),
]

# icon accent per family (RGB); tier decides the halo
EMBER, FROST, THUNDER, VENOM, BLOOD, WYRM, HOLY, SHADOW, EARTH, ASTRAL, LEAF = (255, 140, 50), (150, 215, 255), (175, 145, 255), (130, 230, 90), (230, 60, 60), (200, 90, 255), (255, 225, 120), (110, 110, 170), (210, 165, 100), (90, 160, 255), (120, 210, 120)

def _item(typ, key, tier, base, name, flavor, place, hit=(), mods='', imm='', aura=None, tint=None, value=None, stack=1, recipe=None, **stats):
    return dict(type=typ, key=key, tier=tier, base=base, name=name, flavor=flavor, place=place, hit=list(hit), mods=mods, imm=imm,
                aura=aura, tint=tint, value=value, stack=stack, recipe=recipe, stats=stats)
W = lambda *a, **k: _item('Weapon', *a, **k)
A = lambda *a, **k: _item('Armor', *a, **k)
J = lambda *a, **k: _item('Jewelry', *a, **k)
S = lambda *a, **k: _item('Shield', *a, **k)
R = lambda skill, diff, consumes, mats, sellers, price, final=False: dict(skill=skill, diff=diff, consumes=consumes, mats=mats, sellers=sellers, price=price, final=final)

C, N, L = 'chest', 'npc', 'loot'
FIRE = lambda: ('st', 'burning')
# sellers
FERDOK_SMITH = ('Zwerg_Handwerker_loc02_trainer_graf_schmied', 'location02_grafenstadt')
FUHR_SMITH = ('Handwerker_1_loc02_trainer_fuhr_schmied', 'location02_fuhrmannsheim')
TALLON_CRAFT = ('Handwerkerin_1_loc08_haendler_handwerk', 'location08')
TALLON_MAGE = ('npc_magiertrainer_loc08_trainer_magie', 'location08')
TALLON_HUNTER = ('Jaeger_Kauzenstein_loc08_jaeger', 'location08')
FERDOK_BOWYER = ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')
MUROLOSH_SMITH = ('Zwerg_Handwerker_loc09_schmied', 'location09')
MUROLOSH_MATS = ('Zwerg_Handwerker_loc09_zutatenhaendler', 'location09')
# materials
STEEL, KOSH, DWARF_STEEL, STRIPS, GEMS, GOLD, TINDER, ISINEW, BLOOD_D, TOOTH, SINEW, SCALE = (
    'zutat_s_stahl', 'zutat_s_stahlkoscher', 'zutat_s_stahlzwergen', 'zutat_s_lederbaender', 'zutat_s_edelsteine', 'zutat_s_blattgold',
    'zutat_b_zunderschwamm', 'zutat_b_verbesserte_sehne', 'zutat_a_drachenblut', 'zutat_s_zahndesdrachen', 'zutat_b_drachensehne', 'arm_wyrm_scale')

ITEMS = [
    # ======================= REGULAR: small perks, Avestrue to chapter 3 =======================
    W('r_cutlass', 'regular', 'Entermesser', 'Whetted Cutlass', "A smuggler's cutlass, honed until it sings.",
      (C, 'truhe_01_loc01_botho_lund', 'location01'), hit=[('p', 100, [('dmg', 1, 0, 'physical', '')])], WpATmod=1,
      recipe=R('TaSchmieden', 4, [('Weapon', 'Entermesser', 1)], [(STEEL, 1)], [FERDOK_SMITH, FUHR_SMITH], 3)),
    W('r_skinner', 'regular', 'Dolch', "Huntress' Skinning Knife", 'Kauzenstein keeps it sharp enough to split a hair.',
      [(N, 'Jaeger_Kauzenstein', 'location01'), (N, 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')],
      hit=[('p', 5, [('st', 'wound')])], mods='TaTierkunde +3', value=D(9)),
    W('r_ember_hatchet', 'regular', 'Beil', 'Ember Hatchet', 'The miller used it to split kindling; the wood always caught.',
      (C, 'truhe_kreatur_maultier_01_loc01', 'dungeon01_muehle'), hit=[('p', 8, [FIRE()])], tint=EMBER,
      recipe=R('TaSchmieden', 5, [('Weapon', 'Beil', 1)], [(TINDER, 2)], [FERDOK_SMITH, FUHR_SMITH], 3)),
    W('r_practice_saber', 'regular', 'Saebel', "Amazon's Practice Saber", 'A Kurkum training blade: light, quick and forgiving.',
      [(N, 'bredo_bento_loc01', 'location01'), (N, 'Haendler_3_loc02_haendler_praios_waffen', 'location02_praios')], WpPAmod=1, value=D(15)),
    W('r_watch_cudgel', 'regular', 'Knueppel', 'Cudgel of the Watch', 'Standard issue for the Ferdok watch. Ask any drunk.',
      (C, 'jischka_tot_liegend', 'dungeon02_kanalisation'), hit=[('p', 12, [('st', 'stun')])]),
    W('r_keen_bow', 'regular', 'Kurzbogen', 'Keen Hunting Bow', 'A quick short bow with a waxed silk string.',
      [(N, 'Jaeger_Kauzenstein', 'location01'), (N, 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')],
      hit=[('p', 100, [('dmg', 1, 0, 'physical', '')])], value=D(12)),
    W('r_notched_axe', 'regular', 'Streitaxt', 'Notched Battle Axe', 'Every notch is a story. Most end badly for someone else.',
      (C, 'loc02_kiste_milde_gabe_beute', 'location02_fuhrmannsheim'), hit=[('p', 5, [('st', 'wound')])], tint=BLOOD),
    W('r_balanced_longsword', 'regular', 'Langschwert', 'Balanced Longsword', 'Weighted a finger behind the guard, as the Rondra temple teaches.',
      (N, 'Haendler_3_loc02_haendler_praios_waffen', 'location02_praios'), WpATmod=1, WpINI=1, value=D(22)),
    W('r_vipers_kiss', 'regular', 'Dolch', "Viper's Kiss", 'The Cellar Vault rewards those who reach its last chest.',
      (C, 'loc02_diebespacour_truhe_14', 'dungeon02_diebesgilde'), hit=[('p', 12, [('st', 'poison_weapon')])], tint=VENOM),
    W('r_walking_staff', 'regular', 'kampfstab_02', 'Runed Walking Staff', "A pilgrim's staff with one Hesinde rune burned into the heel.",
      (C, 'truhe_kreatur_skelett_01_loc02_hesinde', 'dungeon02_orakel'), mods='AEmax +10', WpPAmod=1, tint=ASTRAL),
    W('r_tinker_xbow', 'regular', 'Leichte Armbrust', "Tinkerer's Crossbow", 'A dwarf added a ratchet to the winch. Clever, if noisy.',
      (N, 'Zwerg_Zivilist_01_loc02_trainer_graf_armbrust', 'location02_grafenstadt'), WpReload=3, value=D(24)),
    W('r_felling_hatchets', 'regular', 'Wurfbeil', 'Felling Hatchets', 'Throwing hatchets with a heavy, off-centre head.',
      (C, 'loc03_truhe_burg', 'location03'), hit=[('p', 10, [('st', 'overthrown')])], stack=5),
    W('r_boar_spear', 'regular', 'Speer', 'Boar Spear', 'A crossbar below the head stops the beast. Mostly.',
      (C, 'loc04_steinknopf_chest', 'location04'), hit=[('p', 12, [('st', 'overthrown')])], WpPAmod=1),
    W('r_balanced_knives', 'regular', 'Wurfdolch', 'Balanced Throwing Knives', 'Phex-blessed, they say. They certainly fly true.',
      (N, 'Raeuber03_loc02_dieb_haendler', 'location02_praios'), hit=[('p', 100, [('dmg', 1, 0, 'physical', '')])], stack=6, value=D(1)),
    W('r_icicle_foil', 'regular', 'Florett', 'Icicle Foil', 'A blue-white foil that is always cold to the touch.',
      (C, 'loc03_truhe_danor', 'location03'), hit=[('p', 8, [('st', 'corpofrigo')])], tint=FROST),
    A('r_hunters_cap', 'regular', 'helm_lederkappe', "Hunter's Cap", 'A leather cap with a falcon feather and a skinner\'s eye.',
      [(N, 'Jaeger_Kauzenstein', 'location01'), (N, 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')], mods='TaTierkunde +3', value=D(10)),
    A('r_gambeson', 'regular', 'torso_wattierter_waffenrock', 'Avestrue Gambeson', 'Quilted by the village for whoever would stand against the robbers.',
      (C, 'truhe_kreatur_doerfler_01_loc01', 'location01'), RSBr=3),   # review 31 Oct: AU +10 was far too strong early
    A('r_soft_boots', 'regular', 'schuhe_horasischer_einbrecher', "Thief's Soft Boots", 'Felt soles. You hear the guard; the guard does not hear you.',
      [(N, 'Cuano', 'dungeon02_diebesgilde'), (N, 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde')], mods='TaTaschendiebstahl +2', tint=SHADOW, value=D(15)),
    A('r_herbalist_gloves', 'regular', 'handschuhe_tulamide_alchemist', "Herbalist's Gloves", 'Stained fingertips, steady hands.',
      (N, 'Peraine_Priesterin_01_loc02_haendler_graf_kraeuter', 'location02_grafenstadt'), mods='TaAlchimie +3', tint=LEAF, value=D(14)),
    A('r_fletcher_bracers', 'regular', 'armschienen_nieten_01', "Fletcher's Bracers", 'Scored by a thousand fletching knives.',
      (C, 'loc03_truhe_alwene', 'location03'), mods='TaBogenbau +3'),
    A('r_scholar_boots', 'regular', 'schuhe_tulamidischer_elementarist', "Scholar's Travel Boots", 'Embroidered with a rune of study. The left one squeaks.',
      (C, 'loc04_truhe_01_5', 'dungeon04_gruft'), mods='TaMagiekunde +5', tint=ASTRAL),
    A('r_smith_apron', 'regular', 'oberteil_zwerg_sappeur', "Journeyman Smith's Apron", 'Scorched leather with a little hammer stamped on the pocket.',
      (N, 'Zwerg_Handwerker_loc02_trainer_graf_schmied', 'location02_grafenstadt'), mods='TaSchmieden +3', tint=EARTH, value=D(18)),
    J('r_watch_signet', 'regular', 'Silberring', "Watchman's Signet", 'The Ferdok watch notices things. So will you.',
      (C, 'truhe_kreatur_skelett_01_loc02_praios', 'dungeon02_ungluecksrabe'), mods='TaSinnenschaerfe +2 TaMenschenkenntnis +2'),
    J('r_squire_chain', 'regular', 'Silberkette', "Squire's Chain", 'Worn by squires at court. Bow first, then speak.',
      (C, 'roter_schlaechter_tot_liegend', 'dungeon02_orakel'), mods='TaEtikette +3 TaUeberreden +2', tint=HOLY),
    J('r_astral_spring', 'regular', 'Silberring', 'Ring of the Small Astral Spring', 'A moonstone chip that holds a sip of astral power.',
      (N, 'Auralia_loc02_alchimistin_auralia', 'location02_grafenstadt'), mods='AEmax +5', tint=ASTRAL, value=D(20)),
    J('r_hearth_amulet', 'regular', 'Silberkette', "Amulet of Travia's Hearth", 'A tiny tin goose, warm like a kitchen fire.',
      (C, 'truhe_01_loc01_avesschrein', 'location01'), mods='LEmax +2 TaHeilkundeWunden +1', tint=EMBER),
    J('r_phex_ring', 'regular', 'Silberring', "Ring of Phex's Fingers", 'The fox on the seal winks if you look at it sideways.',
      (C, 'loc02_diebespacour_truhe_10', 'dungeon02_diebesgilde'), mods='FF +1 TaSchloesser +2', tint=SHADOW),
    J('r_aves_ring', 'regular', 'Silberring', "Wanderer's Ring of Aves", 'Left at the shrine by a traveller who no longer needed luck.',
      (C, 'truhe_01_loc01_avesschrein', 'location01'), mods='TaWildnisleben +3 TaPflanzenkunde +2', tint=LEAF),
    S('r_watch_buckler', 'regular', 'Holzschild_02', "Watchman's Shield", 'Reinforced oak, painted with the Ferdok colours.',
      [(N, 'staedter_reich_m_01_loc02_haendler_graf_waffen', 'location02_grafenstadt'), (N, 'staedter_reich_m_01_loc02_haendler_graf_waffen_nach_loc05', 'location02_grafenstadt')],
      WpPAmod=1, value=D(16)),
    S('r_hjaldinger_shield', 'regular', 'Thorwaler_Rundschild', 'Hjaldinger Round Shield', 'Thorwalian lime wood, rimmed in iron and salt.',
      (C, 'loc03_truhe_guthof', 'location03'), mods='AUmax +10', WpPAmod=1),

    # ======================= AMAZING: identity effects, mostly craftable from ordinary gear =======================
    W('a_lioncub', 'amazing', 'Amazonensaebel', 'Lioncub Saber', 'A Kurkum saber for an Amazon who has drawn blood but not yet earned her lion.',
      (C, 'loc04_sarkophag_chest_1', 'dungeon04_gruft'), hit=[('p', 12, [('st', 'ArmSundered')])], tint=HOLY),
    W('a_ember_saber', 'amazing', 'Khunchomer', 'Saber of Embers', 'Tulamide fire-steel; the edge glows after every kill.',
      (C, 'loc03_truhe_koch', 'dungeon03_gutshaus_kueche'), hit=[('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 12, [FIRE()])], tint=EMBER,
      recipe=R('TaSchmieden', 10, [('Weapon', 'Khunchomer', 1)], [(TINDER, 3), (KOSH, 1)], [FERDOK_SMITH, TALLON_CRAFT], 8)),
    W('a_bloodletter', 'amazing', 'Bastartschwert', 'Bloodletter', "A bastard sword grooved to keep wounds open.",
      (C, 'loc08_gruft_sarg_tagebuch_03', 'dungeon08_gruft_01'), hit=[('p', 12, [('st', 'ArmBleeding')])], tint=BLOOD,
      recipe=R('TaSchmieden', 12, [('Weapon', 'Bastartschwert', 1)], [(KOSH, 2)], [TALLON_CRAFT], 10)),
    W('a_firuns_kiss', 'amazing', 'Partisane', "Firun's Kiss", 'A partisan forged in a winter so cold the smith lost two fingers.',
      (L, 'loot_dun03_truhe_jost', 'all'), hit=[('p', 12, [('st', 'corpofrigo')]), ('if', 'corpofrigo', [('dmg', 2, 0, 'magic', 'Corpofrigo_Impact')])], tint=FROST,
      recipe=R('TaSchmieden', 11, [('Weapon', 'Partisane', 1)], [(GEMS, 1), (KOSH, 1)], [FERDOK_SMITH, TALLON_CRAFT], 9)),
    W('a_felling_maul', 'amazing', 'Warunker Hammer', 'Felling Maul', 'A two-handed Warunk hammer with a flanged head made to take legs out.',
      (L, 'loot_loc05_truhe_drachenraum_02', 'all'), hit=[('p', 12, [('st', 'stun')]), ('if', 'overthrown', [('dmg', 3, 0, 'physical', 'Niederwerfen')])], tint=EARTH,
      recipe=R('TaSchmieden', 10, [('Weapon', 'Warunker Hammer', 1)], [(STEEL, 2)], [TALLON_CRAFT], 8)),
    W('a_kosch_ember_axe', 'amazing', 'Zwergenskraja', 'Ember Skraja of the Kosch', 'Quenched in the fire of an Angrosch shrine.',
      (L, 'truhe_verschlossen_01_loc05_geheim_endstueck', 'all'), hit=[('p', 12, [FIRE()])], imm='fire', tint=EMBER,
      recipe=R('TaSchmieden', 12, [('Weapon', 'Zwergenskraja', 1)], [(TINDER, 3), (DWARF_STEEL, 1)], [MUROLOSH_SMITH], 10)),
    W('a_thunder_splitter', 'amazing', 'Felsspalter', 'Thunder Stonesplitter', 'Struck by lightning in its own forge. It remembers.',
      (C, 'loc10_chest_zwergenskelett', 'location10'), hit=[('p', 12, [('dmg', 2, 1, 'magic', 'Lightning')])], tint=THUNDER,
      recipe=R('TaSchmieden', 13, [('Weapon', 'Felsspalter', 1)], [(GEMS, 2)], [MUROLOSH_SMITH], 12)),
    W('a_leech_rapier', 'amazing', 'Rapier', 'Leech Rapier', "A duellist's rapier with a hollow, rune-scratched blade.",
      (C, 'loc02_truhe_residenz', 'dungeon02_residenz'), hit=[('p', 25, [('heal', 3)])], WpATmod=1, tint=BLOOD,
      recipe=R('TaSchmieden', 10, [('Weapon', 'Rapier', 1)], [(GOLD, 2), (GEMS, 1)], [FERDOK_SMITH], 9)),
    W('a_starleech_staff', 'amazing', 'Kampfstab', 'Starleech Staff', 'Each blow pulls a thread of power back into its bearer.',
      (C, 'skelett_tot_sitzend_dun08_haendler', 'dungeon08_haendler'), hit=[('p', 100, [('asp', 1)]), ('p', 10, [('st', 'ArmHexed')])], tint=ASTRAL,
      recipe=R('TaBogenbau', 8, [('Weapon', 'Kampfstab', 1)], [(GEMS, 1), (GOLD, 1)], [TALLON_MAGE], 10)),
    W('a_thorn_staff', 'amazing', 'kampfstab_01', "Peraine's Thorn", 'A healer\'s staff of blackthorn. Every blow it lands mends its bearer.',
      (C, 'loc08_gruft_sarg_tagebuch_04', 'dungeon08_gruft_01'), hit=[('p', 20, [('heal', 4)])], mods='LEmax +10', WpPAmod=1, tint=LEAF),
    W('a_ember_longbow', 'amazing', 'Langbogen', 'Ember Longbow', 'Resin-soaked yew. Slow to draw, and the arrows leave sparks.',
      (N, 'Jaeger_Kauzenstein_loc08_jaeger', 'location08'), hit=[('p', 12, [FIRE()])], WpW6plus=5, tint=EMBER, value=D(38),
      recipe=R('TaBogenbau', 12, [('Weapon', 'Langbogen', 1)], [(TINDER, 2), (ISINEW, 1)], [TALLON_HUNTER], 10)),
    W('a_huntress_xbow', 'amazing', 'Leichte Armbrust', "Huntress' Crossbow", 'A light crossbow with a bone stock and a hair trigger.',
      (L, 'loot_loc04_truhe_3', 'all'), hit=[('p', 100, [('dmg', 2, 0, 'physical', '')])], WpReload=3, tint=LEAF,
      recipe=R('TaBogenbau', 9, [('Weapon', 'Leichte Armbrust', 1)], [(ISINEW, 1)], [FERDOK_BOWYER], 7)),
    W('a_felling_xbow', 'amazing', 'Leichte Armbrust', 'Felling Crossbow', 'Its blunt-nosed bolts were made to unhorse knights.',
      (C, 'skelett_tot_sitzend_loc05', 'dungeon05_burg'), hit=[('p', 15, [('st', 'overthrown')])],
      recipe=R('TaBogenbau', 10, [('Weapon', 'Leichte Armbrust', 1)], [('zutat_b_metallteile', 1)], [FERDOK_BOWYER], 8)),
    W('a_ogre_feller', 'amazing', 'Barbarenstreitaxt', 'Ogre-Feller', 'Too heavy for a man and too short for an ogre. Just right for a dwarf.',
      (L, 'loot_loc08_truhe_ogerlager_01', 'none'), hit=[('p', 15, [('st', 'ArmShaken')])], tint=EARTH),
    W('a_viper_fang', 'amazing', 'Schwerer Dolch', 'Viper Fang', 'Its fuller is a channel for venom; the pommel unscrews to refill it.',
      (C, 'loc04_truhe_01_4', 'dungeon04_gruft'), hit=[('p', 20, [('st', 'poison_weapon')]), ('if', 'poison_weapon', [('dmg', 2, 0, 'poison', 'Gift_Impact')])], tint=VENOM,
      recipe=R('TaSchmieden', 9, [('Weapon', 'Schwerer Dolch', 1)], [('zutat_b_giftbeutel', 2)], [FERDOK_SMITH, TALLON_CRAFT], 7)),
    W('a_thunder_shortsword', 'amazing', 'Kurzschwert', 'Short Sword of Thunder', "A legionary's sword etched with a storm-glyph.",
      (C, 'loc08_gruft_sarg_tagebuch_02', 'dungeon08_gruft_01'), hit=[('p', 12, [('dmg', 0, 1, 'magic', 'Lightning')])], WpATmod=1, tint=THUNDER,
      recipe=R('TaSchmieden', 9, [('Weapon', 'Kurzschwert', 1)], [(GEMS, 1)], [FERDOK_SMITH, TALLON_CRAFT], 7)),
    W('a_tide_trident', 'amazing', 'Dreizack', "Efferd's Trident", 'Fished out of the well behind your Ferdok house. Nobody knows how it got there.',
      (C, 'loc02_spielerhaus_brunnen', 'dungeon02_hauptquartier'), hit=[('p', 12, [('st', 'overthrown')]), ('p', 10, [('st', 'corpofrigo')])], tint=FROST),
    S('a_rondra_ward', 'amazing', 'Lederschild', 'Ward of Rondra', "Rondra's lion on a leather shield. Those who carry it do not fall.",
      (C, 'loc03_truhe_burg', 'location03'), imm='overthrown', WpPAmod=1, tint=HOLY),
    A('a_lionheart_helm', 'amazing', 'helm_fluegelhelm_01', 'Lionheart Helm', 'A winged helm whose wearer never takes the first step back.',
      (L, 'loot_unique_Mantra_keh_03_Noldrokon', 'all'), mods='MU +2', tint=HOLY),
    A('a_longshot_bracers', 'amazing', 'arme_elfenschienen_01', 'Bracers of the Long Shot', 'Archer\'s arm guards embossed with a falcon.',
      (L, 'loot_loc04_skelett_sitzend', 'all'), mods='FF +2', tint=LEAF),
    A('a_peraine_gloves', 'amazing', 'handschuhe_verstaerkte_lederruestung', 'Gloves of Peraine', 'Green-dyed leather blessed by the goddess of healing.',
      (N, 'geweihte_peraine_loc08_ulinai', 'location08'), mods='LEmax +10', tint=LEAF, value=D(30)),
    A('a_fox_boots', 'amazing', 'schuhe_nasreddin', 'Fox-step Boots', 'Iryan leather that remembers every root on the forest floor.',
      (N, 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde'), mods='GE +1 AW +1', tint=SHADOW, value=D(34)),
    A('a_astral_robe', 'amazing', 'oberteil_kampfmagier_ferdok', 'Robe of the Astral Tide', 'Silver thread woven in the pattern of the Hesinde tide tables.',
      (N, 'npc_magiertrainer_loc08_trainer_magie', 'location08'), mods='AEmax +10 MR +2', tint=ASTRAL, value=D(40)),
    A('a_ingerimm_apron', 'amazing', 'oberteil_zwergenprospektor', 'Apron of Ingerimm', 'Fireproof leather from a master of the Murolosh forges.',
      (N, 'Zwerg_Handwerker_loc09_schmied', 'location09'), mods='TaSchmieden +6', imm='fire', tint=EMBER, value=D(32)),
    A('a_ironhide_greaves', 'amazing', 'beine_eisenschienen_01', 'Ironhide Greaves', 'Iron greaves that make their wearer heavier to push.',
      (L, 'truhe_verschlossen_01_loc05_geheim_endstueck', 'all'), mods='KO +1', imm='overthrown', tint=EARTH,
      recipe=R('TaSchmieden', 11, [('Armor', 'beine_eisenschienen_01', 1)], [(STEEL, 2), (STRIPS, 2)], [TALLON_CRAFT], 9)),
    A('a_duelist_grips', 'amazing', 'handschuhe_verstaerkte_lederruestung', "Duelist's Grips", 'Separate gloves for a fencer: they pair with arm greaves.',
      (N, 'Haendler_3_loc08_haendler_ruestung', 'location08'), mods='PA +1 GE +1', tint=SHADOW, value=D(30),
      recipe=R('TaSchmieden', 8, [('Armor', 'handschuhe_verstaerkte_lederruestung', 1)], [(STRIPS, 3), (GOLD, 1)], [FERDOK_SMITH, TALLON_CRAFT], 7)),
    A('a_ironfist', 'amazing', 'handschuhe_panzer', 'Ironfist Gauntlets', 'Heavy combined gauntlets for a front-line fighter.',
      (C, 'loc08_gruft_sarg_tagebuch_01', 'dungeon08_gruft_01'), mods='KK +1', RSLA=5, RSRA=5, tint=EARTH,
      recipe=R('TaSchmieden', 12, [('Armor', 'handschuhe_panzer', 1)], [(KOSH, 2)], [TALLON_CRAFT], 10)),
    A('a_iryan_greaves', 'amazing', 'beine_verstaerkte_lederruestung', 'Iryan Half-greaves', 'Hardened leather greaves; no metal, no spell trouble.',
      (N, 'Haendler_3_loc08_haendler_ruestung', 'location08'), mods='KO +1', RSLB=3, RSRB=3, value=D(26),
      recipe=R('TaSchmieden', 9, [('Armor', 'beine_verstaerkte_lederruestung', 1)], [(STRIPS, 3), (STEEL, 1)], [FERDOK_SMITH, TALLON_CRAFT], 7)),
    A('a_ranger_breeches', 'amazing', 'hose_verstaerkte_lederruestung', "Ranger's Reinforced Breeches", 'Double-stitched leather for a fighter who will not wear metal.',
      (C, 'loc08_gruft_sarg_tagebuch_05', 'dungeon08_gruft_01'), mods='GE +1', RSLB=3, RSRB=3,
      recipe=R('TaSchmieden', 8, [('Armor', 'hose_verstaerkte_lederruestung', 1)], [(STRIPS, 3)], [FERDOK_SMITH, TALLON_CRAFT], 6)),
    A('a_adept_mantle', 'amazing', 'schultern_verstaerkte_lederruestung', "Adept's Shoulder-mantle", 'Light shoulder guards stitched with astral thread. Safe for casting.',
      (N, 'npc_magiertrainer_loc08_trainer_magie', 'location08'), mods='AEmax +10', RSLA=2, RSRA=2, ArBE=0.1, tint=ASTRAL, value=D(30),
      recipe=R('TaAlchimie', 9, [('Armor', 'schultern_verstaerkte_lederruestung', 1)], [(GOLD, 2)], [TALLON_MAGE], 8)),
    A('a_spellweaver_breeches', 'amazing', 'hose_thorwaler', "Spellweaver's Breeches", 'Wool breeches embroidered with runes of clear thought.',
      (N, 'npc_magiertrainer_loc08_trainer_magie', 'location08'), mods='IN +1 KL +1', RSLB=2, RSRB=2, tint=ASTRAL, value=D(26),
      recipe=R('TaAlchimie', 9, [('Armor', 'hose_thorwaler', 1)], [(GOLD, 1), (GEMS, 1)], [TALLON_MAGE], 8)),
    J('a_unbowed', 'amazing', 'Silberkette', 'Amulet of the Unbowed', 'A broken chain on a silver thread. You will not kneel.',
      (L, 'loot_unique_Loc03DaVanyaMantraKe', 'all'), mods='AUmax +10', imm='overthrown', tint=HOLY),
    J('a_ox_ring', 'amazing', 'Goldring', 'Ring of the Ox', 'A heavy band of black iron set with a golden ox-head.',
      (C, 'loc08_gruft_sarg_tagebuch_04', 'dungeon08_gruft_01'), mods='KK +1 LEmax +5', tint=EARTH),
    J('a_fletcher_ring', 'amazing', 'Silberring', "Fletcher's Thumb Ring", 'A horn thumb ring that never slips.',
      (N, 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'), mods='TaBogenbau +5 TaBogen +1', tint=LEAF, value=D(14)),
    J('a_summoner_torc', 'amazing', 'Goldkette', "Summoner's Torc", 'A druidic torc of twisted gold; animals come when it hums.',
      (C, 'loc04_truhe_01_4', 'dungeon04_gruft'), mods='ZaTatzeSchwinge +3 ZaSkelettarius +2 ZaElementarerDiener +2 AEmax +5', tint=LEAF),
    J('a_clear_mind', 'amazing', 'Silberring', 'Ring of the Clear Mind', 'A Hesinde-blue sapphire that settles the thoughts.',
      (C, 'loc08_gruft_sarg_tagebuch_01', 'dungeon08_gruft_01'), mods='KL +1 IN +1 TaMagiekunde +3', tint=ASTRAL),
    J('a_salamander_phial', 'amazing', 'Goldkette', 'Salamander Phial', 'A sealed vial on a chain, holding a single living ember.',
      (C, 'zyklop_skelett_tot', 'location11'), mods='MR +1 AEmax +5', imm='fire', tint=EMBER),
    J('a_umbracor_splinter', 'amazing', 'Goldkette', "Splinter of Umbracor's Heart", "A sliver of the good dragon's heart, torn loose when the Purplewyrm fell. Where is the rest?",
      (C, 'loc08a_truhe_japhgur', 'location08_drachenhort'), mods='LEmax +10 AEmax +10', imm='fire', tint=WYRM),

    # ======================= SUPER RARE: build-defining; dwarven and Kurkum sets crafted late =======================
    W('s_rondra_reprimand', 'superrare', 'Amazonensaebel', "Rondra's Reprimand", 'A saber that punishes cowardice and rewards a warrior who presses on.',
      (L, 'loot_loc05_truhe_drachenraum_04', 'all'), hit=[('p', 15, [('st', 'ArmSundered')]), ('if', 'overthrown', [('dmg', 0, 1, 'physical', 'Kulminatio_Impact')]),
       ('p', 8, [('buff', 'ArmTrance')])], WpW6plus=8, WpPAmod=1, tint=HOLY),
    W('s_coalheart', 'superrare', 'Felsspalter', 'Coalheart', 'A two-handed stonesplitter with a core of coal that never cools.',
      (L, 'loot_loc10_geheimraum_02', 'all'), hit=[('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 15, [FIRE()])],
      imm='fire', WpW6plus=6, WpBF=0, tint=EMBER),
    W('s_mountain_patience', 'superrare', 'Zwergenschlaegel', "Mountain's Patience", 'A dwarven maul. The mountain waits, and then it falls on you.',
      (C, 'loc08_bestie_truhe_tatzelwurm', 'dungeon08_bestie'), hit=[('p', 15, [('st', 'stun')]), ('if', 'stun', [('dmg', 0, 1, 'physical', 'Niederwerfen')])],
      WpW6plus=9, WpPAmod=0, tint=EARTH),
    W('s_nightsong', 'superrare', 'Elfenbogen', 'Nightsong', 'A quick Sala elven bow; at night its string hums a lullaby.',
      (C, 'loc08_gruft_sarg_tagebuch_05', 'dungeon08_gruft_01'), hit=[('p', 15, [('st', 'stun')]), ('if', 'stun', [('dmg', 0, 1, 'magic', 'Kulminatio_Impact')])],
      mods='IN +1', WpW6plus=6, tint=LEAF),
    W('s_heartseeker', 'superrare', 'Kriegsbogen', 'Heartseeker', 'A heavy Thorwal war bow. Slow, and it never misses twice.',
      (L, 'loc08a_truhe_arom', 'all'), hit=[('p', 15, [('st', 'ArmBleeding')]), ('p', 10, [('st', 'stun')])], WpW6plus=3, tint=BLOOD),
    W('s_archon_rod', 'superrare', 'Magierstab', "Archon's Rod", "Megalon's old teaching rod. Students learned to dodge it; enemies don't.",
      (C, 'loc03_truhe_da_vanya', 'location03'), hit=[('p', 25, [('st', 'ArmHexed')]), ('p', 100, [('asp', 2)])],
      mods='AEmax +10 MR +2 ZaFulminictus +2 ZaIgnifaxius +2', WpW6plus=4, WpPAmod=1, tint=ASTRAL),
    W('s_phex_whisper', 'superrare', 'Rapier', 'Whisper of Phex', 'Stolen from a Horasian count by someone who left a fox as a calling card.',
      (C, 'loc02_diebespacour_truhe_13', 'dungeon02_diebesgilde'), hit=[('p', 15, [('st', 'ArmDazed')]), ('if', 'ArmDazed', [('dmg', 3, 0, 'physical', '')])],
      mods='TaTaschendiebstahl +2', WpW6plus=5, WpATmod=1, WpINI=2, tint=SHADOW),
    W('s_tusk', 'superrare', 'Jagdspiess', 'Tusk of the Sow-King', 'Carved from the tusk of the boar that ate an Albernian village.',
      (L, 'loot_loc05_truhe_drachenraum_02', 'all'), hit=[('p', 15, [('st', 'overthrown')]), ('p', 12, [('st', 'ArmBleeding')])], WpW6plus=8, tint=BLOOD),
    W('s_thunderbolt', 'superrare', 'Schwere Armbrust', 'Thunderbolt', 'A dwarven siege crossbow. The bolt arrives before the thunder.',
      (C, 'loc10_zwergenschatz', 'location10'), hit=[('p', 100, [('dmg', 0, 1, 'magic', 'Lightning')]), ('p', 20, [('st', 'stun')])], WpReload=5, tint=THUNDER),
    W('s_widowmaker', 'superrare', 'Zweihaender', 'Widowmaker', 'A mercenary two-hander with a ricasso wrapped in black leather.',
      (L, 'truhe_verschlossen_01_loc05_geheim_alchemi', 'all'), hit=[('p', 15, [('st', 'ArmBleeding')]), ('p', 10, [('st', 'overthrown')])], WpW6plus=6, tint=BLOOD),
    A('s_sentinel_mail', 'superrare', 'torso_kettenhemd_lang', 'Mail of the Silver Falls Sentinel', 'The last sentinel of the castle died standing.',
      (C, 'skelett_tot_sitzend_loc05', 'dungeon05_burg'), mods='LEmax +10 KO +1', imm='overthrown', tint=HOLY),
    A('s_thinking_cap', 'superrare', 'hut_magierhut', "Hesinde's Thinking Cap", 'A tall hat whose stars rearrange themselves while you think.',
      (C, 'skelett_tot_sitzend_dun08_haendler', 'dungeon08_haendler'), mods='AEmax +20 MR +2 KL +1', tint=ASTRAL),
    A('s_dancer_boots', 'superrare', 'schuhe_nasreddin', 'Boots of the Seven-League Dancer', 'Iryan boots whose wearer seems to arrive before setting out.',
      (L, 'loot_unique_Aldessia_feindlich', 'all'), mods='GE +2 AW +2 AUmax +10', tint=LEAF),
    A('s_forge_grips', 'superrare', 'handschuhe_verstaerkte_lederruestung', 'Grips of the Forgefather', 'Every knuckle is a tiny anvil.',
      (L, 'loot_loc09_kiste_aldessia2', 'all'), mods='KK +2 TaSchmieden +3', tint=EARTH),
    A('s_salamander_scale', 'superrare', 'torso_schuppenpanzer', 'Salamander Scale Cuirass', 'Salamander scales riveted over dwarven chain.',
      (C, 'loc11_chest_05', 'location11'), mods='LEmax +10 KO +1', imm='fire', tint=EMBER),
    # magical dwarven set (Forgrimm): Murolosh recipes consuming the native pieces sold in Murolosh
    A('d_gauntlets', 'superrare', 'handschuhe_zwergenruestung', 'Gauntlets of the Mountain King', 'Dwarven gauntlets refolded with Angrosch steel.',
      None, mods='KK +1', RSLA=8, RSRA=8, tint=EARTH,
      recipe=R('TaSchmieden', 14, [('Armor', 'handschuhe_zwergenruestung', 1)], [(DWARF_STEEL, 2), (GEMS, 1)], [MUROLOSH_SMITH], 18)),
    A('d_sabatons', 'superrare', 'schuhe_zwergenruestung', 'Stoneroot Sabatons', 'Plated boots that root their wearer like a mountain.',
      None, mods='AUmax +10', imm='overthrown', RSLB=8, RSRB=8, tint=EARTH,
      recipe=R('TaSchmieden', 14, [('Armor', 'schuhe_zwergenruestung', 1)], [(DWARF_STEEL, 2), (STRIPS, 2)], [MUROLOSH_SMITH], 18)),
    A('d_pauldrons', 'superrare', 'schultern_zwergenruestung', 'Pauldrons of the Hearthguard', 'Shoulder plates of the king\'s hearthguard.',
      (L, 'loot_loc10_geheimraum_02', 'all'), mods='LEmax +10', tint=EARTH,
      recipe=R('TaSchmieden', 13, [('Armor', 'schultern_zwergenruestung', 1)], [(DWARF_STEEL, 1), (STRIPS, 3)], [MUROLOSH_SMITH], 15)),
    A('d_helm', 'superrare', 'helm_zwergenruestung', 'Helm of the Deep Watch', 'A storm cap with a gem set over the brow.',
      None, mods='KO +1 MU +1', RSKo=6, tint=EARTH,
      recipe=R('TaSchmieden', 14, [('Armor', 'helm_zwergenruestung', 1)], [(DWARF_STEEL, 1), (GEMS, 1)], [MUROLOSH_SMITH], 15)),
    A('k_warboots', 'superrare', 'schuhe_aydan', 'Kurkum Warboots', 'The Kurkum plated boots, re-forged to cover the whole leg.',
      None, mods='AUmax +10', RSLB=7, RSRB=7, tint=HOLY,
      recipe=R('TaSchmieden', 12, [('Armor', 'schuhe_aydan', 1)], [(KOSH, 2), (STRIPS, 2)], [TALLON_CRAFT, MUROLOSH_SMITH], 12, final=True)),
    J('s_second_wind', 'superrare', 'Goldring', 'Ring of the Second Wind', "A breath of Rondra's storm caught in a ring.",
      (L, 'loot_loc10_geheimraum_02', 'all'), mods='Reg_LE_freq -3 Reg_AU_freq -3 AUmax +10', tint=LEAF),
    J('s_unshaken_mind', 'superrare', 'Goldkette', 'Amulet of the Unshaken Mind', 'A Psychostabilis glyph sealed in amber.',
      (L, 'loot_unique_Mantra_keh_03_Noldrokon', 'all'), mods='MR +3 TaSelbstbeherrschung +3', imm='crowdcontrol', tint=ASTRAL),
    J('s_falcon_eye', 'superrare', 'Goldring', 'Eye of the Falcon', "A falcon's eye of yellow topaz. Through it, everything is in range.",
      (L, 'loot_loc08_haendler_truhe_04', 'none'), mods='TaBogen +3 TaArmbrust +3 ATW6 +1', tint=HOLY),
    S('s_angrosch_wall', 'superrare', 'Eisenschild_01', 'Wall of Angrosch', 'A kite shield of dwarven steel. Behind it, you are a mountain.',
      (L, 'loot_loc08_bestie_truhe_leiche_04', 'none'), mods='KO +1', imm='overthrown', WpPAmod=2, tint=EARTH),
    J('s_lucky_star', 'superrare', 'Goldring', 'Ring of the Lucky Star', "Phex's own star, they say, fell into a gambler's cup.",
      (L, 'loot_loc08_haendler_truhe_04', 'none'), mods='AW +2 MR +2 CH +1', tint=SHADOW),
    # dragon victory: Murolosh recipes using Heavy Wyrm Scales from Japhgur's hoard (7 scales: three of four)
    A('w_scale_cuirass', 'superrare', 'torso_plattenruestung_01', 'Wyrmscale Cuirass', 'Purplewyrm scales riveted over plate. Heavy, hot and nearly impenetrable.',
      None, mods='LEmax +10', imm='fire', RSBr=7, RSRu=6, RSBa=7, tint=WYRM,
      recipe=R('TaSchmieden', 15, [('Armor', 'torso_plattenruestung_01', 1)], [(SCALE, 3), (DWARF_STEEL, 1)], [MUROLOSH_SMITH], 20)),
    A('w_hide_jerkin', 'superrare', 'torso_lederruestung', 'Wyrmhide Jerkin', 'Flexible scales on dragon-blooded leather. No metal: fighters and casters alike.',
      None, imm='fire;overthrown', RSBr=5, RSRu=5, RSBa=5, ArBE=2.0, tint=WYRM,
      recipe=R('TaSchmieden', 14, [('Armor', 'torso_lederruestung', 1)], [(SCALE, 2), (BLOOD_D, 2), (STRIPS, 4)], [MUROLOSH_SMITH], 18)),
    A('w_blood_robe', 'superrare', 'oberteil_kampfmagier_ferdok', 'Dragonblood Robe', 'A robe soaked in Purplewyrm blood and lined with one scale over the heart.',
      None, mods='AEmax +10 MR +2', imm='fire', RSBr=4, RSRu=4, RSBa=4, tint=WYRM,
      recipe=R('TaAlchimie', 14, [('Armor', 'oberteil_kampfmagier_ferdok', 1)], [(SCALE, 1), (BLOOD_D, 3), (GOLD, 2)], [MUROLOSH_MATS], 18)),
    S('w_scale_shield', 'superrare', 'Eisenschild', 'Wyrmscale Shield', 'Two great scales bolted to an iron shield.',
      None, mods='KO +1', imm='fire', WpPAmod=2, tint=WYRM,
      recipe=R('TaSchmieden', 13, [('Shield', 'Eisenschild', 1)], [(SCALE, 2)], [MUROLOSH_SMITH], 15)),

    # ======================= LEGENDARY: unique finds =======================
    W('l_fang_lioness', 'legendary', 'Amazonensaebel', 'Fang of the Lioness', "Rondra's saber, given to the first Queen of Kurkum.",
      (C, 'loc08a_truhe_japhgur', 'location08_drachenhort'),
      hit=[('p', 20, [('st', 'ArmSundered')]), ('if', 'overthrown', [('dmg', 0, 1, 'physical', 'Kulminatio_Impact')]),
           ('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 10, [('buff', 'ArmLionroar')])],
      mods='MU +2', imm='overthrown', WpW6plus=10, WpATmod=2, WpPAmod=1, WpINI=1, WpBF=0, aura=('AttributoMU_State', 'Skeleton_Root'), tint=HOLY),
    W('l_angrosch_hammer', 'legendary', 'Streitkolben', 'First-Forge Hammer of Angrosch', 'The hammer Angrosch used to forge the first dwarf. It is still warm.',
      (C, 'loc11_chest_05', 'location11'),
      hit=[('p', 15, [('st', 'overthrown')]), ('p', 15, [FIRE()]), ('if', 'overthrown', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 8, [('buff', 'ArmIronskin')])],
      mods='KK +2', imm='fire', WpW6plus=10, WpBF=0, WpATmod=1, aura=('Favilludo_State', 'Skeleton_Root'), tint=EMBER),
    W('l_sala_mandra', 'legendary', 'Elfenbogen', 'Bow of Sala Mandra', 'The quick bow of the elven queen who sang the Salamander to sleep.',
      (C, 'loc08a_truhe_japhgur', 'location08_drachenhort'),
      hit=[('p', 20, [('st', 'corpofrigo')]), ('if', 'corpofrigo', [('dmg', 0, 1, 'magic', 'Kulminatio_Impact')]), ('p', 10, [('st', 'stun')]), ('p', 8, [('buff', 'ArmQuickstep')])],
      mods='IN +2', WpW6=2, WpW6plus=3, aura=('Falkenauge_State', 'Head'), tint=LEAF),
    W('l_eye_hesinde', 'legendary', 'Magierstab', 'Eye of Hesinde', 'A staff topped with a crystal eye that sees the threads of every spell.',
      (C, 'loc10_chest_zwergenskelett', 'location10'),
      hit=[('p', 100, [('asp', 2)]), ('p', 20, [('st', 'ArmHexed')]), ('p', 8, [('buff', 'ArmAstralsurge')])],
      mods='AEmax +10 MR +2 KL +1 IN +1 ZaFulminictus +2 ZaIgnifaxius +2 ZaArmatrutz +1', WpW6plus=6, WpPAmod=2, aura=('AttributoKL_State', 'Skeleton_Root'), tint=ASTRAL),
    W('l_phex_laugh', 'legendary', 'Drachenzahn', "Phex's Last Laugh", 'A dragon-tooth dagger stolen from Japhgur himself. Twice.',
      (L, 'loc08a_truhe_arom', 'all'),
      hit=[('p', 20, [('st', 'ArmDazed')]), ('p', 15, [('st', 'ArmVenom')]), ('if', 'ArmDazed', [('dmg', 0, 1, 'physical', '')]), ('p', 10, [('buff', 'ArmQuickstep')])],
      mods='TaTaschendiebstahl +2 GE +1 FF +1', WpW6plus=6, WpATmod=2, WpINI=2, aura=('Seidenzunge_State', 'Damage_Torso'), tint=SHADOW),
    W('l_wyrmbane', 'legendary', 'Andergaster', 'Wyrmbane', 'The Andergast blade that took the head of the Lindwurm of Gratenfels.',
      (C, 'loc08a_truhe_japhgur', 'location08_drachenhort'),
      hit=[('p', 15, [('st', 'ArmBleeding')]), ('p', 12, [('st', 'overthrown')]), ('p', 8, [('buff', 'ArmTrance')])],
      imm='fire', WpW6=3, WpW6plus=5, WpATmod=1, aura=('Kampf_Offensiv1', 'Head'), tint=WYRM),
    S('l_kurkum_aegis', 'legendary', 'shield_amazonen_kurkum', 'Kurkum Aegis', 'The shield of the Amazon queens. No blow has ever broken it.',
      (L, 'loot_loc05_truhe_drachenraum_04', 'all'), mods='MU +1 LEmax +10', imm='overthrown', WpPAmod=3, aura=('Armatrutz_State', 'Damage_Torso'), tint=HOLY),
    A('l_forgefather_plate', 'legendary', 'torso_zwergenruestung', "Forgefather's Breastplate", 'Dwarven plate of the first king of Murolosh.',
      (C, 'loc10_zwergenschatz', 'location10'), mods='LEmax +10 KO +2 KK +1', imm='fire;overthrown', aura=('AttributoKO_State', 'Skeleton_Root'), tint=EARTH),
    A('l_seven_gazes', 'legendary', 'oberteil_magische_robe', 'Robe of the Seven Gazes', 'Seven eyes are embroidered on it. Some of them blink.',
      (C, 'loc11_chest_05', 'location11'), mods='Reg_AE +1 AEmax +10 MR +2 KL +1 IN +1', aura=('Psychostabilis_State', 'Damage_Torso'), tint=ASTRAL),
    J('l_heart_umbracor', 'mythic', 'Goldkette', 'Heart of Umbracor', "The good dragon's heart, made whole and sealed in the dwarves' amulet vault.",
      (L, 'loot_loc10_amuletttruhe', 'all'), mods='MU +1 KL +1 IN +1 CH +1 FF +1 GE +1 KO +1 KK +1 LEmax +15 AEmax +15', imm='fire',
      aura=('Eiseskaelte_State', 'Skeleton_Root'), tint=BLOOD),

    # ======================= MYTHIC: few dungeon artifacts (deep red) =======================
    W('m_last_oath', 'mythic', 'Drachentoeterhammer', 'Last Oath of the Dragon-Slayer', 'A dragonslayer hammer carried through the Fire Falls by the last of its oath-bound wielders.',
      (C, 'loc11_chest_05', 'location11'), hit=[('p', 10, [('st', 'overthrown')]), ('if', 'overthrown', [('dmg', 0, 1, 'physical', 'Niederwerfen')])],
      mods='KK +1', imm='fire', WpW6plus=8, WpATmod=1, WpPAmod=-4, tint=BLOOD),
    A('m_ashwarden', 'mythic', 'oberteil_kampfmagier_praiot', "Ashwarden's Mantle", 'A light robe that came through the Fire Falls unburnt.',
      (C, 'zyklop_skelett_tot', 'location11'), mods='AEmax +10 MR +2 KL +1', imm='fire', RSBr=4, RSRu=4, RSBa=4, ArBE=0.5, tint=BLOOD),
    S('m_gatekeeper', 'mythic', 'Eisenschild_01', 'Gatekeeper of Gruldur', 'The door-shield of the sealed halls. It has never been passed.',
      (C, 'loc10_zwergenschatz', 'location10'), mods='KO +2 LEmax +10', imm='overthrown', WpPAmod=3, WpATmod=1, tint=BLOOD),
]

# v2.1 additions live in armory_data_v21.py (executed here so they share this namespace)
import os as _os
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v21.py'), encoding='utf-8').read())
ITEMS += ITEMS_V21
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v22.py'), encoding='utf-8').read())
ITEMS += ITEMS_V22
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v23.py'), encoding='utf-8').read())
ITEMS += ITEMS_V23

# ---------------- crafting material ----------------
MATERIALS = [  # key, base item, name, description, value heller, placements [(kind, owner, level, stack)]
    ('wyrm_scale', 'zutat_s_zahndesdrachen', 'Heavy Wyrm Scale', "A scale of the Purplewyrm Japhgur, as large as a shield and harder than steel. Murolosh smiths know what to do with it.",
     300, [('chest', 'loc08a_truhe_japhgur', 'location08_drachenhort', 10)]),   # balance audit A3: 10 (heirloom IV x4, reforges, Wyrm armour)
]
# extra native materials added to the dragon hoard (one more tooth and sinew)
HOARD_EXTRA = [('Item', 'zutat_s_zahndesdrachen', 1), ('Item', 'zutat_b_drachensehne', 1)]
# finite harpy-feather supply (R19)
FEATHER_STOCK = [('Haendlerin_1_loc08_haendler_kraeuter', 'location08', 15), ('Kobold_loc02_kobold_auralia', 'location02_grafenstadt', 15),
                 ('Zwerg_Handwerker_loc09_zutatenhaendler', 'location09', 10)]
# bases added to merchants so consuming recipes stay repeatable (R10)
BASE_STOCK = [('Armor', 'oberteil_kampfmagier_ferdok', 'npc_magiertrainer_loc08_trainer_magie', 'location08'),
              ('Armor', 'hose_thorwaler', 'npc_magiertrainer_loc08_trainer_magie', 'location08'),
              ('Weapon', 'Khunchomer', 'staedter_mittel_loc08_haendler_waffe', 'location08')]

# ---------------- Wyrm upgrade: endgame dragon weapons, each with its own role ----------------
WYRM = [  # id, name, hit, stat deltas
    ('weapon_crafted_unique_kurzschwert', 'Saber of the Wyrm', [('p', 15, [FIRE()]), ('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 8, [('st', 'wound')])],
     {'WpW6plus': 2, 'WpATmod': 1}),
    ('weapon_crafted_unique_wurmspiess', 'Spear of the Wyrm', [('p', 15, [('st', 'overthrown')]), ('if', 'overthrown', [('dmg', 0, 1, 'physical', 'Niederwerfen')]), ('p', 10, [FIRE()])],
     {'WpW6plus': 2, 'WpPAmod': 1}),
    ('weapon_crafted_unique_bogen', 'Bow of the Wyrm', [('p', 100, [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 10, [FIRE()])], {'WpW6plus': 3}),
    ('weapon_crafted_unique_armbrust', 'Crossbow of the Wyrm', [('p', 20, [('st', 'stun')]), ('if', 'stun', [('dmg', 0, 1, 'physical', '')]), ('p', 10, [FIRE()])], {'WpW6plus': 2}),
]

# ---------------- Pal'Na'Thar final quest weapons: modest buff, distinct fire identity ----------------
BURN = [('p', 15, [FIRE()])]
VS_BURN = [('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')])]
CYCLOPS = [  # id, name, hit, stat deltas
    ('weapon_unique_zyklopen_saebel', 'Firesong', BURN + VS_BURN, {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_schwert', 'Flamesong', BURN + VS_BURN, {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_axt', 'Firestrike', BURN + VS_BURN, {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_zweihandschwert', 'Flamestrike', BURN + [('p', 12, [('st', 'overthrown')])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_zweihandaxt', 'Flamefury', BURN + [('p', 12, [('st', 'overthrown')])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_speer', 'Firespike', BURN + [('p', 15, [('st', 'overthrown')])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_schwererdolch', 'Firethorn', BURN + [('p', 10, [('st', 'wound')])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_rapier', 'Sparksting', BURN + [('p', 12, [('st', 'ArmDazed')])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_stab', 'Sparkstrike', BURN + [('p', 100, [('asp', 2)])], {'WpW6plus': 2}),
    ('weapon_unique_zyklopen_bogen', 'Firestorm', BURN + VS_BURN, {'WpW6': 1, 'WpW6plus': -1}),
    ('weapon_unique_zyklopen_armbrust', 'Flamesting', BURN + [('p', 20, [('st', 'stun')])], {'WpW6plus': 2}),
]
# small extra for Rhulana's quest armour (native effect, tooltip-safe)
VANILLA_PE = [('Armor', 'torso_aydan', 'PeMU1', 'Courage +1')]

# ---------------- arrow ladder ----------------
AMMO = [
    ('am_barbed_arrow', 'Pfeil', 'Barbed Arrows', 'Wicked barbs that tear on the way out.', [('p', 12, [('st', 'wound')])], 20,
     'Item/zutat_b_ulmenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/2;Item/zutat_b_gaensefedern/1;', 4, ('Jaeger_Kauzenstein', 'location01'), 4),
    ('am_barbed_bolt', 'Bolzen', 'Barbed Bolts', 'Crossbow bolts with barbed heads.', [('p', 12, [('st', 'wound')])], 20,
     'Item/zutat_b_ulmenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_bolzenspitzen/2;Item/zutat_b_gaensefedern/1;', 4, ('Zwerg_Zivilist_01_loc02_trainer_graf_armbrust', 'location02_grafenstadt'), 4),
    ('am_kosh_arrow', 'Pfeil', 'Kosh-steel Arrows', 'Heads of Kosh steel punch through leather and mail.', [('p', 100, [('dmg', 3, 0, 'physical', '')])], 20,
     'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/zutat_s_stahlkoscher/1;Item/zutat_b_gaensefedern/1;', 9, ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'), 8),
    ('am_thunder_arrow', 'Pfeil', 'Thunderhead Arrows', 'A chip of gemstone in each head stores a spark.', [('p', 100, [('dmg', 0, 1, 'magic', 'Lightning')])], 10,
     'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/1;Item/zutat_b_harpyienfedern/1;Item/zutat_s_edelsteine/1;', 12, ('Jaeger_Kauzenstein_loc08_jaeger', 'location08'), 10),
    ('am_frost_arrow', 'Pfeil', 'Frost-fletched Arrows', "Harpy feathers dipped in meltwater from Firun's glaciers.", [('p', 100, [('dmg', 1, 0, 'magic', '')]), ('p', 20, [('st', 'corpofrigo')])], 10,
     'Item/zutat_b_eibenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/1;Item/zutat_b_harpyienfedern/2;', 12, ('Jaeger_Kauzenstein_loc08_jaeger', 'location08'), 10),
    ('am_dwarf_bolt', 'Bolzen', 'Dwarven Steel Bolts', 'Square-headed bolts of Angrosch steel.', [('p', 100, [('dmg', 4, 0, 'physical', '')]), ('p', 10, [('st', 'overthrown')])], 20,
     'Item/zutat_s_stahlzwergen/1;Item/zutat_b_bolzenspitzen/2;Item/zutat_b_holzleim/1;Item/zutat_b_gaensefedern/1;', 14, ('Zwerg_Handwerker_loc09_schmied', 'location09'), 15),
    ('am_wyrmfang_arrow', 'Pfeil', 'Wyrmfang Arrows', "Tipped with splinters of a dragon's tooth. They burn going in.", [('p', 100, [('dmg', 8, 0, 'fire', 'Ignisphaero_Impact')]), ('p', 15, [FIRE()])], 10,
     'Item/zutat_s_zahndesdrachen/1;Item/zutat_b_drachensehne/1;Item/zutat_b_harpyienfedern/3;Item/zutat_b_holzleim/3;', 16, ('Arom_loc08a', 'location08_drachenhort'), 20),
]

# v2.4 heirloom sets + reforges + Gwendala pass (needs ITEMS/AMMO/MATERIALS above)
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v24.py'), encoding='utf-8').read())
ITEMS += ITEMS_V24
AMMO += AMMO_V24

# v2.5 balance audit overrides (last)
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v25.py'), encoding='utf-8').read())
# v2.6 crafting rework (five lines, beast parts) and the armour class rules (last)
exec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v26.py'), encoding='utf-8').read())
