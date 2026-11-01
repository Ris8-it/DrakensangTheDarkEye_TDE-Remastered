# ======================= v2.4: heirloom sets (31 Oct) =======================
import re
# Executed inside armory_data.py (shares its namespace). One set per party member:
#   4 unique pieces hunted across the game (chests, boss loot, Crimson Circle duelists via secret_quests),
#   1 heirloom that grows in 4 stages (recipes: stage II in Tallon, III and IV in Murolosh; IV needs a Heavy Wyrm Scale),
#   a set bonus on the heirloom that grows with the pieces you own (HasItem PlayerParty; re-equip the heirloom after a new piece),
#   and REFORGES: Murolosh recipes that turn a legendary weapon you found into its final mythic form (loot stays the base).
# Rules kept: metal only for heavy fighters (Rhulana, Forgrimm); Gwendala and the Arcane Thief wear leather/cloth;
# dwarven plated boots 8, Kurkum boots 7; never elven buckskin boots; endgame materials from Japhgur, recipes in Murolosh;
# nothing on Drakensang Mountain, nothing in pickpocket tables.

MUROLOSH_WEAPONS = ('Zwerg_Zivilist_02_loc09_waffenhaendler', 'location09')
FERDOK_ELF = ('npc_elfentrainer', 'location02_praios')
HARPY, ELFWOOD, ALCOHOL = 'zutat_b_harpyienfedern', 'zutat_b_elfenholz', 'zutat_a_alkohol'
TATZEL = 'arm_tr_tatzel_fang'

def _h(key, tier, base, name, flavor, place, mods, recipe=None, imm='', aura=None, tint=None):
    return J(key, tier, base, name, flavor, place, mods=mods, imm=imm, aura=aura, tint=tint, recipe=recipe)

ITEMS_V24 = [
    # ======================= RHULANA: Regalia of the Lion Queen (heavy, metal) =======================
    _h('h_rh1', 'amazing', 'Goldkette', "Lion's Tooth of Kurkum", "Rhulana: \"My mother wore this when she took her lioness oath. I thought it was lost.\" It waits for the Queen's regalia.",
       (C, 'chest_schatztruhe_01_loc02_chest_mactalaenata', 'dungeon02_taverne_goldene_lanze'), 'TaSaebel +1 AUmax +3', tint=HOLY),
    _h('h_rh2', 'superrare', 'Goldkette', 'Mane of the Lioness', 'The tooth, bound in a mane of braided gold. Rhulana stands a little taller wearing it.',
       None, 'MU +1 AT +1 TaSaebel +1', tint=HOLY,
       recipe=R('TaSchmieden', 10, [('Jewelry', 'arm_h_rh1', 1)], [(TATZEL, 1), (GOLD, 2)], [TALLON_CRAFT], 12, final=True)),
    _h('h_rh3', 'legendary', 'Goldkette', 'Pride of Kurkum', 'Dwarven gold around a Kurkum oath. "Rondra hears every word sworn on this," says Rhulana.',
       None, 'MU +2 AT +1 PA +1 TaSaebel +2', aura=('AttributoMU_State', 'Skeleton_Root'), tint=HOLY,
       recipe=R('TaSchmieden', 13, [('Jewelry', 'arm_h_rh2', 1)], [(DWARF_STEEL, 1), (GOLD, 2), (GEMS, 1)], [MUROLOSH_SMITH], 20, final=True)),
    _h('h_rh4', 'mythic', 'Goldkette', 'Heart of the Lion Queen', 'A scale of Japhgur set in the Queen\'s gold. The first Lion Queen of Kurkum wore nothing finer.',
       None, 'MU +3 AT +2 PA +2 LEmax +10 TaSaebel +2', imm='overthrown', aura=('AttributoMU_State', 'Skeleton_Root'), tint=BLOOD,
       recipe=R('TaSchmieden', 15, [('Jewelry', 'arm_h_rh3', 1)], [(SCALE, 1), (GOLD, 3), (GEMS, 2)], [MUROLOSH_SMITH], 30, final=True)),
    A('lq_helm', 'superrare', 'helm_aydan', "Lion Queen's Crest-Helm", 'A Kurkum helm with a golden lion crest. Part of the Regalia of the Lion Queen.',
      (L, 'loot_unique_npc_gen_mactaleaenata_anfuehrerin', 'all'), mods='MU +1 PA +1', RSKo=6, tint=HOLY),
    A('lq_cuirass', 'legendary', 'torso_aydan', "Lion Queen's Cuirass", 'Gilded plate over red leather. Sabeth stole it when Kurkum cast her out. Part of the Regalia of the Lion Queen.',
      None, mods='LEmax +10 KO +1', RSBr=7, RSRu=6, RSBa=7, RSLA=1, RSRA=1, RSLB=1, RSRB=1, ArBE=1.5, tint=HOLY),
    A('lq_grips', 'superrare', 'handschuhe_verstaerkte_lederruestung', "Lion Queen's Grips", 'Red leather sword-grips with gilded knuckles. Part of the Regalia of the Lion Queen.',
      (C, 'skelett_tot_sitzend_loc05', 'dungeon05_burg'), mods='AT +1 GE +1', RSLA=3, RSRA=3, tint=HOLY),
    A('lq_sabatons', 'legendary', 'schuhe_aydan', "Lion Queen's Sabatons", 'Kurkum plated boots worked with lion claws. Part of the Regalia of the Lion Queen.',
      (L, 'loot_unique_Aldessia_feindlich', 'all'), mods='GE +1 AW +1', imm='overthrown', RSLB=7, RSRB=7, tint=HOLY),

    # ======================= FORGRIMM: Ferolax's Forge-Panoply (heavy, metal) =======================
    _h('h_fo1', 'amazing', 'Goldring', "Ferolax's Hammer-Ring", 'Forgrimm: "My father\'s ring. I have worn it since the day he died, and I will wear it until it is worthy of him." It waits for the panoply of Ferolax.',
       ('pc', 'pc_forgrimm', 'dungeon02_taverne_silberkrug'), 'TaSchmieden +2 TaZwHiebwaffen +1', tint=EARTH),   # Forgrimm carries it when he joins
    _h('h_fo2', 'superrare', 'Goldring', 'Anvil-Ring of Ferolax', 'Reforged on a Tallon anvil. Forgrimm grumbles that the work is sloppy, and wears it anyway.',
       None, 'KK +1 KO +1 TaSchmieden +2', tint=EARTH,
       recipe=R('TaSchmieden', 10, [('Jewelry', 'arm_h_fo1', 1)], [(KOSH, 2), (GOLD, 1)], [TALLON_CRAFT], 12, final=True)),
    _h('h_fo3', 'legendary', 'Goldring', 'Forgefire Ring', 'Dwarven steel from Murolosh, folded the way Ferolax taught. "Now that," says Forgrimm, "is a ring."',
       None, 'KK +2 KO +1 LEmax +5 TaSchmieden +3', aura=('AttributoKK_State', 'Skeleton_Root'), tint=EARTH,
       recipe=R('TaSchmieden', 13, [('Jewelry', 'arm_h_fo2', 1)], [(DWARF_STEEL, 2), (GEMS, 1)], [MUROLOSH_SMITH], 20, final=True)),
    _h('h_fo4', 'mythic', 'Goldring', "Ferolax's Unbroken Oath", 'Quenched in dragon blood around a sliver of Japhgur\'s scale. Ferolax swore to forge it and never could. His son did.',
       None, 'KK +3 KO +2 LEmax +10', imm='fire', aura=('AttributoKK_State', 'Skeleton_Root'), tint=BLOOD,
       recipe=R('TaSchmieden', 15, [('Jewelry', 'arm_h_fo3', 1)], [(SCALE, 1), (DWARF_STEEL, 2), (BLOOD_D, 1)], [MUROLOSH_SMITH], 30, final=True)),
    A('fx_helm', 'superrare', 'helm_zwerg_drachentoeter', "Ferolax's Crown-Helm", 'The dragonslayer helm of Ferolax. Grimbart took it into exile. Part of Ferolax\'s Forge-Panoply.',
      None, mods='KO +1 MR +1', RSKo=7, tint=EARTH),
    A('fx_plate', 'legendary', 'torso_zwergenruestung', "Ferolax's Forge-Plate", 'Dwarven plate with an anvil worked into the chest. Part of Ferolax\'s Forge-Panoply.',
      (C, 'loc10_zwergenschatz', 'location10'), mods='LEmax +10 KK +1', RSBr=8, RSRu=7, RSBa=8, RSLA=3, RSRA=3, ArBE=3.0, tint=EARTH),
    A('fx_gauntlets', 'superrare', 'handschuhe_zwergenruestung', "Ferolax's Gauntlets", 'Heavy dwarven gauntlets, still black from his forge. Part of Ferolax\'s Forge-Panoply.',
      (C, 'loc10_chest_zwergenskelett', 'location10'), mods='AT +1 KK +1', RSLA=8, RSRA=8, tint=EARTH),
    A('fx_boots', 'legendary', 'schuhe_zwergenruestung', "Ferolax's Plated Boots", 'Dwarven plated boots that have never taken a step back. Part of Ferolax\'s Forge-Panoply.',
      (C, 'loc11_chest_feuerbruecke_03', 'location11'), mods='KO +1', imm='overthrown', RSLB=8, RSRB=8, tint=EARTH),

    # ======================= GWENDALA: Moonwarden's Raiment (light, leather) =======================
    _h('h_gw1', 'amazing', 'Silberkette', 'Seed of the Moon-Tree', 'Gwendala: "A moon-tree seed. My people plant one for every warden. Someone carried mine all the way to this marsh."',
       (C, 'loc04_steinknopf_chest', 'location04'), 'TaBogen +1 TaSinnenschaerfe +2', tint=LEAF),
    _h('h_gw2', 'superrare', 'Silberkette', 'Song of Sala', 'The seed has sprouted in its silver cage. It hums an elven song nobody taught it.',
       None, 'IN +1 FF +1 TaBogen +1', tint=LEAF,
       recipe=R('TaBogenbau', 10, [('Jewelry', 'arm_h_gw1', 1)], [(HARPY, 2), (ELFWOOD, 1)], [TALLON_HUNTER], 12, final=True)),
    _h('h_gw3', 'legendary', 'Silberkette', "Moonwarden's Oath", 'A moon-tree sapling the size of a finger. Gwendala says it can see in the dark. She is not joking.',
       None, 'IN +2 FF +1 AW +1 TaBogen +2', aura=('Falkenauge_State', 'Head'), tint=LEAF,
       recipe=R('TaBogenbau', 13, [('Jewelry', 'arm_h_gw2', 1)], [(GEMS, 1), (ELFWOOD, 1), (ISINEW, 1)], [MUROLOSH_WEAPONS], 20, final=True)),
    _h('h_gw4', 'mythic', 'Silberkette', "Sala Mandra's Last Song", 'The moon-tree blossoms around a dragon scale, as in the song of the queen who sang the Salamander to sleep.',
       None, 'IN +3 FF +2 GE +1 AW +2 TaBogen +2', imm='poison', aura=('Falkenauge_State', 'Head'), tint=BLOOD,
       recipe=R('TaBogenbau', 15, [('Jewelry', 'arm_h_gw3', 1)], [(SCALE, 1), (SINEW, 1), (GEMS, 1)], [MUROLOSH_WEAPONS], 30, final=True)),
    A('mw_hood', 'superrare', 'hut_jaeger', "Moonwarden's Hood", 'A grey-green hunter\'s hood. Faelwen took it from a warden he sold. Part of the Moonwarden\'s Raiment.',
      None, mods='IN +1 TaSinnenschaerfe +2', RSKo=2, tint=LEAF),
    A('mw_jerkin', 'legendary', 'oberteil_elfenkaempfer', "Moonwarden's Jerkin", 'Elven leather that drinks moonlight. Its owner\'s ghost still haunts the hollow tree where she died. Part of the Moonwarden\'s Raiment.',
      (L, 'loot_loc04_skelett_sitzend', 'all'), mods='GE +1 AEmax +5', RSBr=4, RSRu=3, RSBa=4, RSLA=2, RSRA=2, ArBE=0.5, tint=LEAF),
    A('mw_bracers', 'superrare', 'handschuhe_nasreddin', "Moonwarden's Bracers", 'Iryan leather bracers stitched with silver leaves. Part of the Moonwarden\'s Raiment.',
      (C, 'skelett_tot_sitzend_dun08_haendler', 'dungeon08_haendler'), mods='FF +1 TaBogen +1', RSLA=3, RSRA=3, tint=LEAF),
    A('mw_treads', 'legendary', 'schuhe_nasreddin', "Moonwarden's Treads", 'Soft Iryan boots that leave no track. Part of the Moonwarden\'s Raiment.',
      (C, 'loc11_chest_feuerbruecke_02', 'location11'), mods='GE +1 AW +1', RSLB=4, RSRB=4, tint=LEAF),

    # ======================= ARCANE THIEF: The Stolen Grimoire (light, leather/cloth, caster) =======================
    _h('h_th1', 'amazing', 'Silberkette', 'Grimoire Locket', 'A locket holding one page of the grimoire you stole in Grangor. The rest of the book is out there, and it wants to be whole.',
       (C, 'loc02_truhe_bibliothek_aventurischer_bote', 'dungeon02_bibliothek'), 'AEmax +5 TaMagiekunde +1', tint=ASTRAL),
    _h('h_th2', 'superrare', 'Silberkette', 'The Stolen Grimoire', 'The locket has grown into a tiny book on a chain. New pages appear in it at night, in your handwriting.',
       None, 'KL +1 AEmax +10 TaMagiekunde +2', tint=ASTRAL,
       recipe=R('TaAlchimie', 10, [('Jewelry', 'arm_h_th1', 1)], [(GEMS, 1), (ALCOHOL, 1), (GOLD, 1)], [TALLON_MAGE], 12, final=True)),
    _h('h_th3', 'legendary', 'Silberkette', 'Grimoire of the Margins', 'Every margin is full of notes by every thief who ever owned it. Some of them are spells.',
       None, 'KL +2 IN +1 AEmax +10 Reg_AE +1 TaMagiekunde +3', aura=('AttributoKL_State', 'Skeleton_Root'), tint=ASTRAL,
       recipe=R('TaAlchimie', 13, [('Jewelry', 'arm_h_th2', 1)], [(GEMS, 2), (GOLD, 2)], [MUROLOSH_MATS], 20, final=True)),
    _h('h_th4', 'mythic', 'Silberkette', 'The Unwritten Page', 'Bound in a dragon scale, the grimoire is finally whole, and its last page is blank. It is waiting for you to write it.',
       None, 'KL +2 IN +2 GE +1 AEmax +15 Reg_AE +1 MR +2', aura=('AttributoKL_State', 'Skeleton_Root'), tint=BLOOD,
       recipe=R('TaAlchimie', 15, [('Jewelry', 'arm_h_th3', 1)], [(SCALE, 1), (BLOOD_D, 1), (GEMS, 2)], [MUROLOSH_MATS], 30, final=True)),
    A('gt_cowl', 'superrare', 'hut_streuner', "Spellthief's Cowl", 'A wide hat with a hidden pocket for stolen spells. The necromancer of Tallon was wearing it. Part of the Stolen Grimoire.',
      (L, 'loot_unique_npc_untoter_nekromant_loc08_gruft_boss', 'all'), mods='KL +1 AEmax +5', RSKo=2, tint=ASTRAL),
    A('gt_coat', 'legendary', 'torso_verstaerkte_lederruestung', "Spellthief's Coat", 'A dark leather coat lined with pages. Arrows hate it; so do spells. Part of the Stolen Grimoire.',
      (C, 'loc08_gruft_sarg_tagebuch_04', 'dungeon08_gruft_01'), mods='GE +1 MR +2', RSBr=4, RSRu=4, RSBa=4, RSLA=2, RSRA=2, ArBE=1.0, tint=ASTRAL),
    A('gt_gloves', 'superrare', 'handschuhe_des_diebes', 'Ink-Stained Gloves', 'Ravena\'s gloves, stained with ink and older things. Part of the Stolen Grimoire.',
      None, mods='FF +2 TaTaschendiebstahl +2', RSLA=2, RSRA=2, tint=ASTRAL),
    A('gt_boots', 'legendary', 'schuhe_streuner', 'Margin-Walker Boots', 'High boots that walk where the map has no ink. Part of the Stolen Grimoire.',
      (L, 'loot_loc11_truhe_3', 'all'), mods='GE +1 TaSchleichen +3', RSLB=3, RSRB=3, tint=ASTRAL),

    # ======================= Gwendala pass: more bows and archer gear =======================
    W('a_moonbow', 'amazing', 'Elfenbogen', 'Moonbow', 'A pale elven bow. Its arrows find what the night hides.',
      (N, *FERDOK_ELF), hit=[('p', 15, [('st', 'ArmDazed')])], mods='IN +1', WpW6plus=2, value=D(40), tint=LEAF),
    W('a_hawkstring', 'amazing', 'Kurzbogen', 'Hawkstring', 'A short bow strung with hawk-gut. Quick as a stoop.',
      (N, *TALLON_HUNTER), hit=[('p', 100, [('dmg', 1, 0, 'physical', '')])], WpW6plus=2, WpINI=2, value=D(36), tint=LEAF),
    W('s_thornwood', 'superrare', 'Kriegsbogen', 'Thornwood Warbow', 'A heavy war bow of black thornwood. Its arrows leave the wound open.',
      (C, 'hesperia_schuttberg', 'dungeon08_haendler'), hit=[('p', 15, [('st', 'ArmBleeding')]), ('p', 10, [('st', 'overthrown')])], WpW6plus=4, tint=BLOOD),
    W('s_silverleaf', 'superrare', 'weapon_crafted_elfenbogen', 'Silverleaf Longbow', 'A longbow of silverleaf. Frost gathers on the string.',
      (L, 'loot_unique_Alwene', 'all'), hit=[('p', 12, [('st', 'corpofrigo')]), ('if', 'corpofrigo', [('dmg', 0, 1, 'magic', 'Corpofrigo_Impact')])], mods='FF +1', WpW6plus=3, tint=FROST),
    A('a_moonglove', 'amazing', 'handschuhe_elfen', "Archer's Moon-Glove", 'A soft elven shooting glove with a silver finger-guard.',
      (N, *FERDOK_ELF), mods='FF +1 TaBogen +2', value=D(30), tint=LEAF),
]

# extra arrows for Gwendala (same shape as AMMO in armory_data.py)
AMMO_V24 = [
    ('am_moonsilver_arrow', 'Pfeil', 'Moonsilver Arrows', 'Silver-tipped: the dead fear them.', [('race', 'Untoter', [('dmg', 2, 1, 'magic', 'Kulminatio_Impact')])], 20,
     'Item/zutat_b_ulmenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/2;Item/zutat_b_gaensefedern/1;Item/zutat_s_edelsteine/1;', 8, ('npc_elfentrainer', 'location02_praios'), 6),
    ('am_hawk_arrow', 'Pfeil', 'Hawk-feather Arrows', 'Fletched with hawk feathers: they bite deeper.', [('p', 100, [('dmg', 1, 0, 'physical', '')])], 20,
     'Item/zutat_b_ulmenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/2;Item/zutat_b_harpyienfedern/1;', 8, ('Jaeger_Kauzenstein_loc08_jaeger', 'location08'), 6),
    ('am_sleepthorn_arrow', 'Pfeil', 'Sleepthorn Arrows', 'Tipped with sleepthorn sap: the target staggers.', [('p', 15, [('st', 'stun')])], 20,
     'Item/zutat_b_ulmenholz/1;Item/zutat_b_holzleim/1;Item/zutat_b_pfeilspitzen/2;Item/zutat_b_gaensefedern/1;Item/zutat_a_alkohol/1;', 9, ('Jaeger_Kauzenstein_loc08_jaeger', 'location08'), 7),
]

# set bonuses: heirloom stage -> (pieces, per-piece bonus, full-set bonus or None, label)
_RH = ['arm_lq_helm', 'arm_lq_cuirass', 'arm_lq_grips', 'arm_lq_sabatons']
_FO = ['arm_fx_helm', 'arm_fx_plate', 'arm_fx_gauntlets', 'arm_fx_boots']
_GW = ['arm_mw_hood', 'arm_mw_jerkin', 'arm_mw_bracers', 'arm_mw_treads']
_TH = ['arm_gt_cowl', 'arm_gt_coat', 'arm_gt_gloves', 'arm_gt_boots']
SETS_V24 = {
    'h_rh2': (_RH, 'LEmax +3', None, 'Regalia of the Lion Queen'), 'h_rh3': (_RH, 'LEmax +4', 'AT +1 PA +1', 'Regalia of the Lion Queen'),
    'h_rh4': (_RH, 'LEmax +5', 'AT +2 PA +2 GE +1', 'Regalia of the Lion Queen'),
    'h_fo2': (_FO, 'LEmax +3', None, "Ferolax's Forge-Panoply"), 'h_fo3': (_FO, 'LEmax +4', 'AT +1 KO +1', "Ferolax's Forge-Panoply"),
    'h_fo4': (_FO, 'LEmax +5', 'AT +2 KK +1 KO +1', "Ferolax's Forge-Panoply"),
    'h_gw2': (_GW, 'AUmax +4', None, "Moonwarden's Raiment"), 'h_gw3': (_GW, 'AUmax +5', 'FF +1 AW +1', "Moonwarden's Raiment"),
    'h_gw4': (_GW, 'AUmax +6', 'FF +1 IN +1 AW +2', "Moonwarden's Raiment"),
    'h_th2': (_TH, 'AEmax +3', None, 'The Stolen Grimoire'), 'h_th3': (_TH, 'AEmax +4', 'GE +1 AW +1', 'The Stolen Grimoire'),
    'h_th4': (_TH, 'AEmax +5', 'GE +1 AW +2 AT +1', 'The Stolen Grimoire'),
}
# pieces dropped by Crimson Circle duelists (added to their loot tables by build_secret_quests.py)
DUELIST_PIECES = {'sabeth': 'arm_lq_cuirass', 'grimbart': 'arm_fx_helm', 'faelwen': 'arm_mw_hood', 'ravena': 'arm_gt_gloves'}

# ======================= REFORGES: a found legendary -> its final mythic form (Murolosh, one Heavy Wyrm Scale) =======================
REFORGES = [  # new key, source key, name, flavor, extra procs, extra mods, recipe skill, mats, seller
    ('m_rf_lion_queen', 'l_fang_lioness', 'Fang of the Lion Queen', "Rondra's saber, reforged with a scale of Japhgur. Rhulana: \"Now Kurkum will sing of us.\"",
     [('p', 12, [('st', 'wound')])], 'GE +1', 'TaSchmieden', [(DWARF_STEEL, 2), (GOLD, 2)], MUROLOSH_SMITH),
    ('m_rf_rondra_verdict', 'l_lionsbane', "Rondra's Verdict", "Sabeth's saber, purified and reforged. The outcast's blade now judges for Kurkum.",
     [('if', 'ArmSundered', [('dmg', 2, 1, 'physical', '')])], 'PA +1', 'TaSchmieden', [(DWARF_STEEL, 2), (GOLD, 2)], MUROLOSH_SMITH),
    ('m_rf_last_oath', 'm_last_oath', 'Last Oath, Fulfilled', 'The dragonslayer hammer, finished at last with the scale of the dragon it was sworn against.',
     [('p', 12, [('st', 'wound')])], 'KO +1', 'TaSchmieden', [(DWARF_STEEL, 2), (BLOOD_D, 1)], MUROLOSH_SMITH),
    ('m_rf_exile', 'l_exile_cleaver', 'Cleaver of the Returned Exile', "Grimbart's axe, reforged in Murolosh. Forgrimm brought it home; the exile's name is spoken again.",
     [('p', 12, [('st', 'wound')])], 'MU +1', 'TaSchmieden', [(DWARF_STEEL, 2), (BLOOD_D, 1)], MUROLOSH_SMITH),
    ('m_rf_sala', 'l_sala_mandra', "Sala Mandra's Lullaby", "The elven queen's bow, restrung with dragon sinew. Its arrows sing their targets to sleep.",
     [('p', 15, [('st', 'stun')])], 'GE +1', 'TaBogenbau', [(SINEW, 1), (ELFWOOD, 1)], MUROLOSH_WEAPONS),
    ('m_rf_duskarrow', 'l_duskarrow', 'Duskarrow Redeemed', "Faelwen's bow, reborn in Gwendala's hands. It hunts only those who hunt elves now.",
     [('p', 12, [('st', 'ArmBleeding')])], 'IN +1', 'TaBogenbau', [(SINEW, 1), (ELFWOOD, 1)], MUROLOSH_WEAPONS),
    ('m_rf_crimson', 'm_crimson_vow', 'Crimson Vow, Unbroken', "Ravena's dirk, reforged around a scale. The Circle's oath is yours alone now.",
     [('p', 10, [('buff', 'ArmAstralsurge')])], 'KL +1', 'TaSchmieden', [(DWARF_STEEL, 1), (GEMS, 2)], MUROLOSH_SMITH),
    ('m_rf_phex', 'l_phex_laugh', "Phex's Final Jest", 'The dragon-tooth dagger, stolen from Japhgur twice, finally fitted with a piece of Japhgur. Phex is delighted.',
     [('p', 15, [('st', 'ArmShadowstep')]), ('p', 10, [('st', 'wound')])], 'FF +1', 'TaSchmieden', [(DWARF_STEEL, 1), (GEMS, 2)], MUROLOSH_SMITH),
]
_SRC = {it['key']: it for it in ITEMS}
for key, src, name, flavor, procs, mods, skill, mats, seller in REFORGES:
    s = _SRC[src]
    st = dict(s['stats'])
    st['WpW6plus'] = st.get('WpW6plus', 0) + (2 if skill == 'TaBogenbau' else 3)
    st['WpATmod'] = st.get('WpATmod', 0) + 1
    _sum = {}
    for _a, _sg, _n in re.findall(r'(\w+) ([+-])(\d+)', f"{s['mods']} {mods}"): _sum[_a] = _sum.get(_a, 0) + int(_sg + _n)
    allmods = ' '.join(f'{_a} {_v:+d}' for _a, _v in _sum.items())
    ITEMS_V24.append(W(key, 'mythic', s['base'], name, flavor, None, hit=list(s['hit']) + procs, mods=allmods, imm=s['imm'], aura=s['aura'], tint=BLOOD,
                       recipe=R(skill, 15, [('Weapon', f'arm_{src}', 1)], [(SCALE, 1)] + mats, [seller], 35, final=True), **st))
