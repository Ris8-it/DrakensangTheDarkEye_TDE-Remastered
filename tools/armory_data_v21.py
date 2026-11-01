# ======================= v2.1: Arcane Thief line, throwing weapons, off-hands, Nightfox set, helpers, bosses =======================
# Appended to ITEMS by armory_data.py. Same DSL as the main list.

ITEMS_V21 = [
    # off-hands (shield slot, safe buckler mesh)
    S('r_spellguard', 'regular', 'Buckler', 'Spellguard Buckler', 'A small buckler of rune-carved horn and leather for duellists who also cast. No metal: it does not hinder spellcasting.',
      [(N, 'Cuano', 'dungeon02_diebesgilde'), (N, 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde')], mods='AEmax +5', WpPAmod=1, ArMaterial='Wood', tint=ASTRAL, value=D(18)),
    S('a_nightfox_buckler', 'amazing', 'Buckler', 'Nightfox Buckler', 'Blackened ironwood, quiet and light. It turns blades and curses alike. No metal: it does not hinder spellcasting.',
      (L, 'loot_unique_Skelett_alrico_farfara_loc04', 'all'), mods='AW +1 MR +2', WpPAmod=2, ArMaterial='Wood', tint=SHADOW),
    S('s_mirror_buckler', 'superrare', 'Buckler', 'Phexian Mirror-Buckler', 'Lacquered so bright it shines like a mirror; spells glance off it. No metal: it does not hinder spellcasting.',
      (C, 'loc10_chest_zwergenskelett', 'location10'), mods='MR +3 AEmax +10', imm='fire', WpPAmod=2, WpATmod=1, ArMaterial='Wood', tint=SHADOW),
    # throwing line: big stacks, cheap recipes that make 10
    W('a_hexknives', 'amazing', 'Wurfmesser', 'Hexing Knives', 'Throwing knives scratched with a curse-rune.',
      (L, 'loot_unique_ferio_drachenkultist', 'all'), hit=[('p', 100, [('dmg', 2, 0, 'magic', '')]), ('p', 12, [('st', 'ArmHexed')])], stack=15, tint=ASTRAL,
      recipe=R('TaSchmieden', 7, [], [(STEEL, 1), (GOLD, 1)], [FERDOK_SMITH, TALLON_CRAFT], 6)),
    W('a_starfall', 'amazing', 'Wurfsterne', 'Starfall Stars', 'Throwing stars that flash like falling stars as they strike.',
      [(N, 'Raeuber03_loc02_dieb_haendler', 'location02_praios'), (N, 'Raeuber03_loc08_haendler_dieb', 'location08')],
      hit=[('p', 100, [('dmg', 0, 1, 'magic', 'Lightning')]), ('p', 15, [('st', 'ArmDazed')])], stack=20, tint=THUNDER, value=D(1),
      recipe=R('TaSchmieden', 9, [], [(STEEL, 1), (GEMS, 1)], [TALLON_CRAFT], 8)),
    W('s_witchfire', 'superrare', 'Wurfdolch', 'Witchfire Daggers', 'Balanced daggers with a hollow core of salamander oil.',
      (C, 'loc08_bestie_truhe_tatzelwurm', 'dungeon08_bestie'), hit=[('p', 100, [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 15, [FIRE()])], stack=15, tint=EMBER,
      recipe=R('TaSchmieden', 11, [], [(KOSH, 1), (TINDER, 2)], [MUROLOSH_SMITH], 12)),
    # Arcane Thief daggers
    W('a_spellthief_dirk', 'amazing', 'Langdolch', "Spellthief's Dirk", "Each cut steals a spark of the victim's power.",
      (L, 'loot_unique_wagnitz_drachenkultist_loc03', 'all'), hit=[('p', 100, [('asp', 1)]), ('p', 12, [('st', 'ArmHexed')])], mods='AEmax +5', tint=ASTRAL,
      recipe=R('TaSchmieden', 9, [('Weapon', 'Langdolch', 1)], [(GEMS, 1)], [FERDOK_SMITH, TALLON_CRAFT], 8)),
    W('s_nightfang', 'superrare', 'weapon_special_elfisches_langmesser', 'Nightfang', 'A black elven knife; its first strike blinds.',
      (C, 'loc08_gruft_sarg_tagebuch_02', 'dungeon08_gruft_01'), hit=[('p', 15, [('st', 'blitzDichFind')]), ('if', 'blitzDichFind', [('dmg', 0, 1, 'physical', '')]),
       ('p', 8, [('buff', 'ArmQuickstep')])], mods='AW +1', WpW6plus=6, WpATmod=1, WpINI=2, tint=SHADOW),
    # Nightfox set: leather, spell-safe, the Arcane Thief's alternative to the final quest armour
    A('n_hood', 'amazing', 'helm_verstaerkte_lederruestung', 'Nightfox Hood', 'A deep leather hood with a ward sewn into the lining.',
      (N, 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde'), mods='MR +2 TaSchleichen +2', tint=SHADOW, value=D(24)),
    A('n_gloves', 'amazing', 'handschuhe_des_diebes', 'Nightfox Gloves', 'Fingerless at the tips, for locks and spellwork.',
      (C, 'loc04_truhe_01_5', 'dungeon04_gruft'), mods='FF +2 TaSchloesser +2 AEmax +5', tint=SHADOW),
    A('n_breeches', 'amazing', 'hose_horasischer_einbrecher', 'Nightfox Breeches', 'Soft breeches with hidden pockets and a quilted lining.',
      (C, 'skelett_tot_sitzend_loc05', 'dungeon05_burg'), mods='AEmax +5 MR +1 TaTaschendiebstahl +2', RSLB=2, RSRB=2, tint=SHADOW),
    A('n_jerkin', 'superrare', 'shadow_armor', 'Nightfox Jerkin', 'Shadow leather worked with astral thread: fighters wear it for the cut, casters for the cast.',
      (L, 'loot_unique_npc_untoter_nekromant_loc08_gruft_boss', 'all'), mods='GE +2 AEmax +10 AW +1', RSBr=4, RSRu=4, RSBa=4, tint=SHADOW),
    A('n_treads', 'superrare', 'schuhe_nasreddin', 'Nightfox Treads', 'Iryan leather boots that never creak.',
      (N, 'Zwerg_Zivilist_02_loc09_gemischtwarenhaendler', 'location09'), mods='GE +1 AW +1 TaSchleichen +3', tint=SHADOW, value=D(40)),
    J('n_signet', 'superrare', 'Goldring', 'Nightfox Signet', 'The seal of a guild that does not exist. Phex knows.',
      (L, 'loot_loc10_geheimraum_02', 'all'), mods='AEmax +10 MR +2 TaTaschendiebstahl +2 TaSchloesser +2', tint=SHADOW),
    # crafting helpers: just enough that no dedicated crafter is required
    J('r_artisan_band', 'regular', 'Silberring', "Artisan's Band", 'A guild ring engraved with three tiny tools: hammer, knife, scale.',
      [(N, 'Zwerg_Handwerker_loc02_trainer_graf_schmied', 'location02_grafenstadt'), (N, 'Handwerkerin_1_loc08_haendler_handwerk', 'location08')],
      mods='TaSchmieden +2 TaBogenbau +2 TaAlchimie +2', tint=EARTH, value=D(16)),
    J('a_masterwork_band', 'amazing', 'Goldring', "Master Artisan's Band", 'The same three tools, in gold. Murolosh smiths nod when they see it.',
      (N, 'Zwerg_Handwerker_loc09_schmied', 'location09'), mods='TaSchmieden +4 TaBogenbau +4 TaAlchimie +4', tint=EARTH, value=D(30)),
    # boss signatures and party additions
    J('a_amazon_torc', 'amazing', 'Goldkette', 'Torc of the Free Amazons', 'Taken from the Mactaleanata leader. Rhulana knows what it means.',
      (L, 'loot_unique_npc_gen_mactaleaenata_anfuehrerin', 'all'), mods='AUmax +10 TaSaebel +1', tint=HOLY),
    J('a_valonion_string', 'amazing', 'Silberring', "Valonion's Bowstring Ring", 'A ring wound from the string of an elven bow.',
      (L, 'loot_unique_Mantra_keh_02_valonion', 'all'), mods='TaBogen +2 FF +1', tint=LEAF),
    A('g_salamander_robe', 'superrare', 'oberteil_waldelfenrobe', 'Robe of the Salamander Singer', 'An elven robe for an archer who sings spells between shots.',
      (L, 'loot_loc04_skelett_sitzend', 'all'), mods='AEmax +10 IN +1 TaBogen +1 MU +1 GE +1 FF +1', tint=LEAF),
    A('k_helm', 'superrare', 'helm_aydan', 'Helm of the Lioness Queen', 'The Kurkum helmet, re-forged with a golden lion crest.',
      None, mods='MU +1 AUmax +10', RSKo=5, tint=HOLY,
      recipe=R('TaSchmieden', 12, [('Armor', 'helm_aydan', 1)], [(KOSH, 1), (GOLD, 2)], [TALLON_CRAFT, MUROLOSH_SMITH], 12, final=True)),
]
# native crafting tools added to early shops (re-buyable helpers)
TOOL_STOCK = [('Weapon', 'weapon_schmiedehammer_klein', 'Zwerg_Handwerker_loc02_trainer_graf_schmied', 'location02_grafenstadt'),
              ('Weapon', 'Schnitzmesser', 'Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'),
              ('Jewelry', 'special_feinwaage', 'Auralia_loc02_alchimistin_auralia', 'location02_grafenstadt'),
              ('Jewelry', 'special_feinwaage', 'Kobold_loc02_kobold_auralia', 'location02_grafenstadt')]
RECIPE_EASE = 2   # every recipe difficulty lowered by this (crafting is hard without a specialist)
