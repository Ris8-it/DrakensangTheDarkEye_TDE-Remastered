"""Drakensang TDE Remastered - systems module (installs AFTER mods/armory_v2; uses its Arm* effects and arm_* items).
Trophies from skinning, trophy talismans, weapon oils, traps, wands, scrolls, skill-check weapons, living-weapon chains, set bonuses.
Usage: python -I tools/build_remastered.py "<game>/export/db/armory_backup" mods/remastered_systems
"""
import sys, os, re, shutil
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, Block, U, lit, insert, mods_text, procs_text, build_procs, make_icon, ACT, NATIVE_OK

db, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(__file__)
m = Mod(db, 'remastered')
D = lambda d: int(d * 100)
ARMORY_SE = {'ArmSundered': 'Sundered Guard', 'ArmShaken': 'Shaken', 'ArmBleeding': 'Bleeding', 'ArmHexed': 'Hexed', 'ArmDazed': 'Dazed',
             'ArmVenom': 'Wyrm Venom', 'ArmTrance': 'Battle Trance', 'ArmLionroar': "Lion's Roar", 'ArmIronskin': 'Iron Skin',
             'ArmSecondwind': 'Second Wind', 'ArmAstralsurge': 'Astral Surge', 'ArmQuickstep': 'Quickstep', 'ArmShadowstep': 'Shadowstep',
             'ArmFrailty': 'Frailty', 'ArmStarburn': 'Starburn'}
m.se_names.update(ARMORY_SE)
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
ICONS_VANILLA = os.path.join(HERE, 'research', 'out', 'icons_vanilla')
ART = os.path.join(HERE, '..', 'assets', 'remastered_icons')
icon_files, catalogue = [], []
SKILL = {'TaSchmieden': 'Smithing', 'TaBogenbau': 'Bowcraft', 'TaAlchimie': 'Alchemy', 'TaMagiekunde': 'Arcane lore'}
OTTO = ('holzfaeller_loc02_haendler_graf_fliegender', 'location02_grafenstadt')   # Crooked Otto: all wolf plans (review 1 Nov)
HUNTERS = [('Jaeger_Kauzenstein', 'location01'), ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'), ('Jaeger_Kauzenstein_loc08_jaeger', 'location08')]
ALCH = [('Auralia_loc02_alchimistin_auralia', 'location02_grafenstadt'), ('Kobold_loc02_kobold_auralia', 'location02_grafenstadt'), ('Haendlerin_1_loc08_haendler_kraeuter', 'location08')]
MAGE = [('npc_magiertrainer_loc08_trainer_magie', 'location08')]
SMITHS = [('Zwerg_Handwerker_loc02_trainer_graf_schmied', 'location02_grafenstadt'), ('Handwerkerin_1_loc08_haendler_handwerk', 'location08')]
MUROLOSH = [('Zwerg_Handwerker_loc09_schmied', 'location09')]
TALLON_THIEF = ('Raeuber03_loc08_haendler_dieb', 'location08')

def icon(key, base_brush, tier, tint=None):
    custom = os.path.join(ART, f'arm_{key}.dds')
    if os.path.isfile(custom):
        shutil.copy2(custom, os.path.join(out, 'icons', f'arm_{key}.dds')); icon_files.append(f'arm_{key}.dds'); return f'icons/arm_{key}'
    src = os.path.join(ICONS_VANILLA, base_brush.split('/')[-1].lower() + '.dds')
    if not os.path.exists(src): src = os.path.join(ICONS_VANILLA, base_brush.split('/')[-1] + '.dds')
    if not os.path.exists(src): src = os.path.join(ICONS_VANILLA, 'magic_amulett_01.dds')   # always ship our own file so art can be swapped later
    make_icon(src, os.path.join(out, 'icons', f'arm_{key}.dds'), tier, tint); icon_files.append(f'arm_{key}.dds')
    return f'icons/arm_{key}'
def name_of(typ, iid):
    if iid.startswith('arm_'): return NAMES.get(iid) or PACK_NAMES.get(iid, iid)
    lk = m.s.execute(f'select LookAtText from _Template_{typ} where Id=?', (iid,)).fetchone()
    assert lk, (typ, iid)
    return m.l.execute('select LocaText from _Locale where LocaId=?', (lk[0],)).fetchone()[0]
NAMES = {}
from dsa import pack_names
PACK_NAMES = pack_names(os.path.join(HERE, '..'))   # armory_v2 names for recipes that consume armory items
def recipe(key, result_typ, result_id, result_name, skill, diff, ingredients, sellers, price, batch=1, preview=''):
    rid = f'arm_rezept_{key}'
    ingr = ''.join(f'{t}/{i}/{n};' for t, i, n in ingredients)
    txt = (f"{SKILL[skill]} {diff}. Makes {str(batch) + ' ' if batch > 1 else ''}{result_name}." + (f"\\n{preview}" if preview else '')
           + "\\nConsumes: " + ', '.join(f'{n} {name_of(t, i)}' for t, i, n in ingredients) + '.')
    rbase = {'TaSchmieden': 'rezept_baerenfalle', 'TaBogenbau': 'rezept_schlingenfalle', 'TaAlchimie': 'rezept_waffenbalsam'}.get(skill) or \
        m.s.execute('select Id from _Template_Recipe where TaAttr=? limit 1', (skill,)).fetchone()[0]
    m.template('Recipe', rbase, rid, f'Plans: {result_name}', txt, RecipeIngredients=ingr, RecipeResult=f'{result_typ}/{result_id}/{batch}',
               Difficulty=diff, TaAttr=skill, Value=D(price), IconBrush=m.recipe_icon(result_typ, result_id, skill))
    for o, l in sellers: m.place('Recipe', rid, 'npc', o, l)
def limited(lid, execute, target, script, short, long):
    row = dict(Id=lid, ExecuteOn=execute, Target=target, ScriptFilename=script, ShortDescription=f'{lid}_short', LongDescription=f'{lid}_long', PossibleCharacteristikas='all')
    m.static += [f"DELETE FROM _Template_LimitedScripts WHERE Id={lit(lid)};", insert('_Template_LimitedScripts', row)]
    m.undo_static.append(f"DELETE FROM _Template_LimitedScripts WHERE Id={lit(lid)};")
    m.text(f'{lid}_short', short); m.text(f'{lid}_long', long)
def action_script(name, kids_builder):
    b = Block(f'remastered/act/{name}'); b.begin(kids_builder(b))
    m.static.append(f'-- action {name}'); m.emit_block(b)
    m.static.append(insert('_Scripts_ActionScripts', dict(ScriptName=name, StatementRef=b.ref, StatementBlock=b.guid)))
    m.undo_static.append(f"DELETE FROM _Scripts_ActionScripts WHERE ScriptName={lit(name)};")
    return name

# ======================= statuses (long scroll buffs) =======================
for sid, nm, desc, mods, dur, se, hp, tex in (
        ('ArmScrollHaste', 'Haste (scroll)', 'Agility +2, Dodge +2, Attack +1.', 'GE +2 AW +2 AT +1', 60, 'Axxeleratus_State', 'Skeleton_Root', 'status_fx_spell_axxeleratus'),
        ('ArmScrollShadow', 'Shadow Veil (scroll)', 'Dodge +3, Sneak +5.', 'AW +3 TaSchleichen +5', 60, 'Seidenzunge_State', 'Damage_Torso', 'status_fx_spell_ecliptifactus'),
        ('ArmScrollIron', 'Iron Skin (scroll)', 'Parry +2, Dodge +2, Magic resistance +2.', 'PA +2 AW +2 MR +2', 60, 'Armatrutz_State', 'Damage_Torso', 'status_fx_spell_armatrutz'),
        ('ArmScrollTrance', 'Battle Trance (scroll)', 'Attack +2, Parry +1, Courage +2.', 'AT +2 PA +1 MU +2', 60, 'Kampf_Offensiv1', 'Head', 'status_fx_spell_kampfrausch')):
    m.status(sid, nm, desc, start=mods, duration=dur, state_effect=se, hardpoint=hp, texture=tex, categories='buff;good')
m.status('ArmScrollMend', 'Mending (scroll)', 'Regains 3 LE every 3 seconds, ten times.', duration=0,
         ticks=[f'Heal fixedLE="3" dice="6" diceAmount="0" {ACT}', 'WaitAction duration="3" permanent="false" actionSelection="script"; '] * 10,
         state_effect='Balsam_State', hardpoint='Skeleton_Root', texture='status_fx_regenerierend', categories='buff;good')

# ======================= trophies (skinning with Animal Lore) =======================
TROPHIES = [  # key, name, description, value heller
    ('tr_wolf_fang', 'Wolf Fang', 'A long, yellowed canine. Hunters wear them; talisman-makers want them.', 15),
    ('tr_boar_tusk', 'Boar Tusk', 'A curved tusk, still sharp at the tip.', 25),
    ('tr_bear_claw', 'Bear Claw', 'A claw as long as a finger. Bears do not give these up willingly.', 40),
    ('tr_spider_eye', 'Glittering Green Eye', 'A faceted green eye from something with far too many legs. It still seems to watch you.', 60),
    ('tr_scorpion_sting', 'Scorpion Stinger', 'The venom bladder is still half full. Handle with care.', 50),
    ('tr_crab_plate', 'Crab Shell Plate', 'A plate of giant-crab shell, hard as horn and cold to the touch.', 35),
    ('tr_toad_wart', 'Troll-toad Wart', 'A bitter, rubbery wart. Alchemists swear by its sap.', 30),
    ('tr_firefly_sac', 'Firefly Ember Sac', 'A glowing sac from a giant firefly. It is warm and smells of sulphur.', 45),
    ('tr_louse_carapace', 'Crypt-louse Carapace', 'A shard of chitin from the crypt lice. Dead magic clings to it.', 40),
    ('tr_rat_tail', "Giant Rat's Tail", 'A scaly tail as thick as a rope, from a rat that grew far too big. Thieves pay for luck like this.', 80),
    ('tr_tatzel_fang', 'Tatzelwurm Fang', 'A fang from a tatzelwurm, a lesser cousin of the dragons.', 150),
    ('tr_wyrm_horn', 'Purplewyrm Horn', "A horn from Japhgur's brow. It hums faintly with the dragon's power.", 300),
    ('tr_whitefur_fang', 'Fang of White Fur', 'The great fang of White Fur, the pale wolf of the Dark Forest. A hunter could build a legend on it.', 60),
]
for key, nm, desc, val in TROPHIES:
    iid = f'arm_{key}'; NAMES[iid] = nm
    m.template('Item', 'zutat_a_giftzahn', iid, nm, desc + '\\n\\nTrophy: crafting material for talismans, oils and traps.', Value=val, Gew=10,
               IconBrush=icon(key, 'icons/alchimie_zutat_giftzahn', 'regular'))
# skinning tables: fill the empty "big beast" tables, add trophies to the existing ones
SKIN = {  # table fragment -> trophies (chance, amount)
    'skin_wolf_klein': [('tr_wolf_fang', 60, 1)], 'skin_wolf_mittel': [('tr_wolf_fang', 75, 1)], 'skin_wolf_weissfell': [('tr_wolf_fang', 100, 2)],
    'skin_wolf_gro': [('tr_wolf_fang', 100, 2)], 'skin_wildschwein_klein': [('tr_boar_tusk', 60, 1)], 'skin_wildschwein_mittel': [('tr_boar_tusk', 75, 1)],
    'skin_wildschwein_gro': [('tr_boar_tusk', 100, 2)], 'skin_baer_klein': [('tr_bear_claw', 75, 1)], 'skin_baer_mittel': [('tr_bear_claw', 100, 1)],
    'skin_baer_gro': [('tr_bear_claw', 100, 2)], 'skin_smaragdspinne_klein': [('tr_spider_eye', 60, 1)], 'skin_smaragdspinne_gro': [('tr_spider_eye', 100, 2)],
    'skin_riesenskorpion_klein': [('tr_scorpion_sting', 75, 1)], 'skin_riesenskorpion_gro': [('tr_scorpion_sting', 100, 2)],
    'skin_riesenkrabbe_klein': [('tr_crab_plate', 75, 1)], 'skin_riesenkrabbe_gro': [('tr_crab_plate', 100, 2)],
    'skin_trollkroete_klein': [('tr_toad_wart', 75, 1)], 'skin_trollkroete_gro': [('tr_toad_wart', 100, 2)],
    'skin_feuerfliege_gro': [('tr_firefly_sac', 100, 2)], 'skin_gruftassel_klein': [('tr_louse_carapace', 75, 1)],
    'skin_gruftassel_gro': [('tr_louse_carapace', 100, 2)], 'skin_ratte_gro': [('tr_rat_tail', 100, 1)],
    'skin_tatzelwurm': [('tr_tatzel_fang', 100, 2)], 'skin_japhgur': [('tr_wyrm_horn', 100, 1)],
}
used = {r[0] for r in m.s.execute("select FurriersLootTable from _Template_Monster where FurriersLootTable<>'' union select FurriersLootTable from _Template_NPC where FurriersLootTable<>''")} \
    if 'FurriersLootTable' in [c[1] for c in m.s.execute('pragma table_info(_Template_NPC)')] else \
    {r[0] for r in m.s.execute("select FurriersLootTable from _Template_Monster where FurriersLootTable<>''")}
used |= {r[0] for r in m.g.execute("select FurriersLootTable from _Instance_Monster where FurriersLootTable<>''")}
skin_rows = []
for frag, entries in SKIN.items():
    names = sorted(n for n in used if n == frag or (frag.endswith('_gro') and n.startswith(frag)))
    assert names, frag
    for tname in names:
        exists = tname in m.loot_tables()
        content = ''.join(f'Item/arm_{k}/{c}/{n}/0/;' for k, c, n in entries)
        if exists:
            for k, c, n in entries: m.loot(tname, 'Item', f'arm_{k}', mode='plus1', chance=c, amount=n)
        else:   # empty "big beast" table the game references but never defined
            m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(tname)};",
                         insert('_DSA_LootTables', dict(LootTableName=tname, LootTableValue=str(len(entries)), LootTableContent=content))]
            m.undo_static.append(f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(tname)};")
        skin_rows.append((tname, ', '.join(NAMES[f'arm_{k}'] for k, _, _ in entries), 'new table' if not exists else 'added'))


# ======================= item stories (review 2 Nov): every craftable is a small piece of the world =======================
DESC_R = {
    'tl_wolf': "Three wolf fangs on a leather thong, the way Avestrue boys wear them after their first hunt. The old hunters say wolves can smell it and keep their distance, out of respect or embarrassment.",
    'tl_boar': "A pair of boar tusks bound in silver wire. Farmhands wear these at harvest: a boar never gives up, and neither do they.",
    'tl_rat': "A ring cut from the tail of a rat that grew far too big. Ferdok's thieves swear by them: rats always find a way in, and always a way out.",
    'tl_bear': "Two bear claws set in gold, the talisman of the old forest hunters. Bears do not fight for long. They do not need to.",
    'tl_spider': "A glittering green eye from something with far too many legs, set in gold. It sees venom coming and tells the blood to ignore it.",
    'tl_scorpion': "A ring of scorpion stinger from the dwarves' mushroom gardens, where the scorpions grow fat on the warmth. Quick as a sting, and just as sudden.",
    'tl_firefly': "A still-warm ember sac from a giant firefly, sealed in a gold locket. Fire does not bite the one who carries a piece of it.",
    'tl_tatzel': "A tatzelwurm fang bound in gold leaf. The beasts never back down from a fight, and neither does whoever wears this.",
    'tl_wyrm': "A horn from the brow of the great purple wyrm, bound in gold. Its strength hums in the chest like a second heartbeat.",
    'tl_ward1': "A disc of giant-crab shell on a leather thong, carried by Ferdok's harbour men against bad luck. Blows and curses alike glance off it.",
    'tl_ward2': "A crab-shell disc rubbed with bitter troll-toad sap by a Moorbridge druid. Spells slide off it like rain off a thatched roof.",
    'tl_ward3': "Crypt-louse chitin layered over shell and sap. It drinks dead magic and never seems to get full.",
    'oil_frost': "A pale blue oil pressed from crab shell. The blade frosts over as it is applied, and so does whatever it cuts.",
    'oil_ember': "Firefly sap stirred into fat: the blade smoulders for ten blows and leaves burns that will not close.",
    'oil_venom': "Spider venom thickened with fat by Tallon's herb-woman, who will not say who taught her.",
    'oil_frailty': "Troll-toad sap that seeps into wounds and steals the strength from them. It smells worse than it works, which is saying something.",
    'oil_holy': "Spring water blessed at a Praios shrine. The dead burn where it touches them, and the living feel strangely accused.",
    'oil_thunder': "Crushed gemstone and charcoal: an alchemist's joke that stopped being funny. Every blow cracks like lightning.",
    'trap_frost': "A snare of crab shell and sinew that freezes what it catches, invented by a harbour trapper tired of losing eels.",
    'trap_web': "Sticky spider silk stretched between two pegs. It drops a foe and saps their strength, the way the spider likes it.",
    'trap_venom': "Spikes smeared with scorpion venom: a dwarven gardener's answer to scorpions in the mushroom beds.",
    'trap_thunder': "A gemstone primed with a spark inside an iron cup. It goes off with a crack of thunder and a lot of swearing.",
    'trap_hex': "A rune drawn in gold leaf to a witch's recipe. Whoever steps on it is cursed and terrified, in that order.",
    'trap_wyrmfire': "Dragon blood and tinder in an iron shell. The dwarves who invented it lost two workshops proving it works.",
    'wand_ember': "A charred wand tipped with a firefly sac, made by a Tallon apprentice who could not light a candle any other way.",
    'wand_frost': "A wand of white wood capped with crab shell. Moorbridge fishermen used one to keep their catch cold, until a mage noticed.",
    'wand_thunder': "An iron rod wrapped in copper wire by a dwarven tinkerer who wanted to see what a storm looks like up close. It crackles.",
    'wand_wither': "Black bone tipped with crypt-louse chitin, taken from a necromancer's desk. It drains strength and will, as its owner intended.",
    'g_grand_furrier': "A master furrier's knife reforged with dwarven steel and a tatzelwurm fang. No hide is too tough, no claw too stubborn.",
    'g_harvest_sickle': "A druid's golden sickle blessed with gold leaf and a living ember. Every herb it cuts yields a little more, as Peraine intended.",
}
# ======================= talismans (trophies -> jewelry, Bowcraft) =======================
TALISMANS = [  # key, base, name, desc, mods, imm, recipe ingredients, diff, sellers, price
    ('tl_wolf', 'Silberkette', 'Wolf-fang Necklace', 'Three fangs on a thong. The wild feels a little less strange.', 'AUmax +5 TaSchleichen +1', '', [('tr_wolf_fang', 3)], 5, [OTTO], 4),
    ('tl_boar', 'Silberkette', 'Boar-tusk Charm', 'Stubborn as a boar.', 'LEmax +5 TaSelbstbeherrschung +2', '', [('tr_boar_tusk', 2)], 6, HUNTERS[:2], 5),
    ('tl_rat', 'Silberring', "Rat-king's Ring", "Made from a giant rat's tail. Thieves' luck.", 'TaTaschendiebstahl +2 TaSchloesser +2', '', [('tr_rat_tail', 1)], 6, HUNTERS[1:2], 6),
    ('tl_bear', 'Goldkette', 'Bear-claw Talisman', 'The strength of the bear, carried at the throat.', 'AUmax +10 TaEinschuechtern +2', '', [('tr_bear_claw', 2)], 8, HUNTERS[2:], 8),   # audit B6: no early Strength, Tallon only
    ('tl_spider', 'Goldkette', 'Green-eye Amulet', 'A glittering green eye that sees poison coming.', 'IN +1', 'poison', [('tr_spider_eye', 1)], 10, HUNTERS[2:], 10),
    ('tl_scorpion', 'Goldring', 'Scorpion-sting Ring', 'Quick as a sting.', 'FF +1 AT +1', '', [('tr_scorpion_sting', 2)], 10, MUROLOSH, 10),   # scorpions: Murolosh mushroom garden, after Tallon
    ('tl_firefly', 'Goldkette', 'Ember-sac Charm', 'Still warm. Fire does not bite its wearer.', 'AEmax +5', 'fire', [('tr_firefly_sac', 2)], 10, HUNTERS[2:], 10),
    ('tl_tatzel', 'Goldkette', 'Tatzelwurm-fang Amulet', 'Dragon-kin courage: you stand your ground.', 'MU +2', 'overthrown', [('tr_tatzel_fang', 1), ('zutat_s_blattgold', 2)], 12, HUNTERS[2:], 15),
    ('tl_wyrm', 'Goldkette', 'Purplewyrm-horn Talisman', "Japhgur's horn, bound in gold. Its power is now yours.", 'KK +1 KO +1 MU +1 LEmax +10', 'fire', [('tr_wyrm_horn', 1), ('zutat_s_edelsteine', 2)], 14, MUROLOSH, 20),
]
for key, base, nm, desc, mods, imm, ingr, diff, sellers, price in TALISMANS:
    desc = DESC_R.get(key, desc)
    iid = f'arm_{key}'; NAMES[iid] = nm
    lines = ([mods_text(mods)] if mods else []) + ([{'fire': 'Immune to burning', 'poison': 'Immune to poison', 'overthrown': 'Immune to knockdown'}[imm]] if imm else [])
    pe = m.status('PeArm' + key.replace('_', '').capitalize(), nm, '; '.join(lines), start=mods, immunity=imm)
    m.template('Jewelry', base, iid, nm, desc + '\\n\\n' + '\\n'.join(lines), PermanentEffect=pe, Value=D(6), IconBrush=icon(key, 'icons/magic_amulett_01', 'amazing'))
    recipe(key, 'Jewelry', iid, nm, 'TaBogenbau', diff, [('Item', f'arm_{t}' if t.startswith('tr_') else t, n) for t, n in ingr] + [('Item', 'zutat_s_lederbaender', 1)],
           sellers, price, preview='; '.join(lines))
    catalogue.append(('Talisman', nm, '; '.join(lines), f"Bowcraft {diff}: " + ', '.join(f'{n} {NAMES.get("arm_" + t, t)}' for t, n in ingr)))

# White Fur: her fang and Silver Ruff ride in the template's SetupStorage next to the quest pelt (always on the corpse;
# the value-0 loot roll dropped the Ruff in play). Instances carry no SetupStorage, so only the template changes.
WF_STORE = 'Item/loc01_alphaweibchen_fell:1/true/false;'
m.static.append(f"UPDATE _Template_Monster SET SetupStorage={lit(WF_STORE + 'Item/arm_tr_whitefur_fang:1/true/false;Item/arm_tr_silver_ruff:1/true/false;')} WHERE Id='loc01_wolf_weissfell';")
m.undo_static.append(f"UPDATE _Template_Monster SET SetupStorage={lit(WF_STORE)} WHERE Id='loc01_wolf_weissfell';")
m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_whitefur';",
             insert('_DSA_LootTables', dict(LootTableName='arm_lt_whitefur', LootTableValue='1',
                    LootTableContent='Item/arm_tr_wolf_fang/100/2/1/;'))]
# the Wolfpack line (armory_data_v25): dark pelts from skinning the big wolves after the tutorial
for _t, _c in (('skin_wolf_mittel', 35), ('skin_wolf_groß', 100)): m.loot(_t, 'Item', 'arm_tr_darkwolf_pelt', mode='all', chance=_c, amount=1, value=6)   # big wolves always (player, 2 Nov)
m.undo_static.append("DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_whitefur';")
m.edit_vanilla('Monster', 'loc01_wolf_weissfell', LootTable='arm_lt_whitefur')
# upgrade path: Wolf-fang Necklace -> Alpha's Fang Necklace (Crooked Otto, Count's Town, like every wolf plan)
ALPHA = 'AW +1 TaSchleichen +2 AUmax +5'   # review 2 Nov: Dodge instead of Survival, no early attribute
NAMES['arm_tl_wolf_alpha'] = "Alpha's Fang Necklace"
m.template('Jewelry', 'Silberkette', 'arm_tl_wolf_alpha', "Alpha's Fang Necklace",
           "A wolf-fang necklace rebuilt around the great fang of White Fur. You move like the pack leader now: low, quick, and never where the blow lands.\\n\\n" + mods_text(ALPHA),
           PermanentEffect=m.status('PeArmTlwolfalpha', "Alpha's Fang Necklace", mods_text(ALPHA), start=ALPHA), Value=D(10),
           IconBrush=icon('tl_wolf_alpha', 'icons/magic_amulett_01', 'superrare'))
recipe('tl_wolf_alpha', 'Jewelry', 'arm_tl_wolf_alpha', "Alpha's Fang Necklace", 'TaBogenbau', 8,
       [('Jewelry', 'arm_tl_wolf', 1), ('Item', 'arm_tr_whitefur_fang', 1), ('Item', 'arm_tr_wolf_fang', 2)], [OTTO], 8, preview=mods_text(ALPHA))
catalogue.append(('Talisman', "Alpha's Fang Necklace", mods_text(ALPHA), 'Bowcraft 8: Wolf-fang Necklace, Fang of White Fur, 2 Wolf Fangs'))
# Warding Charm I-III (crafting rework 1 Nov): replaces the Crab-shell Ward, Troll-toad Charm and Carapace Charm (three near-duplicates).
# I: crab plates (Ferdok harbour), Otto. II: + troll-toad warts, the Moorbridge druid. III: + crypt-louse carapace, the Tallon hunter.
WARDING = [  # key, base, name, desc, mods, consumes (type, id, n), diff, sellers, price
    ('tl_ward1', 'Silberkette', 'Warding Charm', 'A disc of giant-crab shell on a thong. Blows and curses alike glance off it.', 'PA +1 MR +1',
     [('Item', 'arm_tr_crab_plate', 2), ('Item', 'zutat_s_lederbaender', 1)], 7, [OTTO], 6),
    ('tl_ward2', 'Silberkette', 'Greater Warding Charm', 'The Warding Charm, rubbed with bitter troll-toad sap. Spells slide off like rain off a roof.', 'PA +1 MR +2 KO +1',
     [('Jewelry', 'arm_tl_ward1', 1), ('Item', 'arm_tr_toad_wart', 2)], 9, [('Dorfbewohnerin01_loc04', 'location04')], 9),
    ('tl_ward3', 'Goldkette', 'Grand Warding Charm', 'Crypt-louse chitin over shell and sap. It drinks dead magic and does not get full.', 'PA +1 MR +3 KO +1 AUmax +5',
     [('Jewelry', 'arm_tl_ward2', 1), ('Item', 'arm_tr_louse_carapace', 2)], 11, HUNTERS[2:], 12),
]
for key, base, nm, desc, mods, ingr, diff, sellers, price in WARDING:
    desc = DESC_R.get(key, desc)
    iid = f'arm_{key}'; NAMES[iid] = nm
    m.template('Jewelry', base, iid, nm, desc + '\n\n' + mods_text(mods), PermanentEffect=m.status('PeArm' + key.replace('_', '').capitalize(), nm, mods_text(mods), start=mods),
               Value=D(4 + 3 * int(key[-1])), IconBrush=icon(key, 'icons/magic_amulett_01', ('amazing', 'superrare', 'legendary')[int(key[-1]) - 1]))
    recipe(key, 'Jewelry', iid, nm, 'TaBogenbau', diff, ingr, sellers, price, preview=mods_text(mods))
    catalogue.append(('Talisman', nm, mods_text(mods), f"Bowcraft {diff}: " + ', '.join(f'{n} {NAMES.get(i, i)}' for _, i, n in ingr)))
# Wolf-fang Necklace II (player, 2 Nov): the mad pack's moon sinew rebinds the fangs; the plan comes with Hagen's trapper notes
_k, _nm, _mods = 'tl_wolf2', 'Moonhowl Pendant', 'AUmax +8 TaSchleichen +2 MU +1'
_desc = "The wolf-fang necklace restrung on moon-mad sinew, with a fourth fang from Alvina's wolves. Wolves hear it before they see you, and think twice."
NAMES['arm_tl_wolf2'] = _nm
m.template('Jewelry', 'Silberkette', 'arm_tl_wolf2', _nm, _desc + '\n\n' + mods_text(_mods), PermanentEffect=m.status('PeArmTlwolf2', _nm, mods_text(_mods), start=_mods),
           Value=D(10), IconBrush=icon('tl_wolf2', 'icons/magic_amulett_01', 'superrare'))
recipe('tl_wolf2', 'Jewelry', 'arm_tl_wolf2', _nm, 'TaBogenbau', 9,
       [('Jewelry', 'arm_tl_wolf', 1), ('Item', 'arm_tr_moon_sinew', 1), ('Item', 'arm_tr_wolf_fang', 2)], [], 10, preview=mods_text(_mods))
catalogue.append(('Talisman', _nm, mods_text(_mods), 'Bowcraft 9: Wolf-fang Necklace, 1 moon sinew, 2 wolf fangs (plan from Hagen)'))
# Rhulana (review 2): Animal Lore 9 base = 5 after her Tulamide/Amazon rules (-4), so she can skin early with a knife
_rt = m.g.execute("select TaTierkunde from _Instance_PC where Name='Rhulana'").fetchone()[0]
m.game.append("UPDATE _Instance_PC SET TaTierkunde=9 WHERE Name='Rhulana';")
m.undo_game.append(f"UPDATE _Instance_PC SET TaTierkunde={_rt} WHERE Name='Rhulana';")

# ======================= weapon oils (10 charges, whetstone pattern) =======================
OILS = [  # key, name, desc, hit procs, ingredients, diff
    ('oil_frost', 'Frostbite Oil', 'A pale blue oil that frosts the blade.', [('p', 100, [('dmg', 1, 0, 'magic', '')]), ('p', 20, [('st', 'corpofrigo')])], [('arm_tr_crab_plate', 1), ('zutat_a_salbenfett', 1)], 8),
    ('oil_ember', 'Ember Oil', 'Firefly sap: the blade smoulders.', [('p', 100, [('dmg', 1, 0, 'fire', '')]), ('p', 25, [('st', 'burning')])], [('arm_tr_firefly_sac', 1), ('zutat_a_salbenfett', 1)], 8),
    ('oil_venom', 'Spider Venom Oil', 'Spider venom, thickened with fat.', [('p', 25, [('st', 'ArmVenom')])], [('arm_tr_spider_eye', 1), ('zutat_a_giftzahn', 1), ('zutat_a_salbenfett', 1)], 10),
    ('oil_frailty', 'Bonecrusher Paste', 'Troll-toad sap that saps the strength from wounds.', [('p', 20, [('st', 'ArmFrailty')])], [('arm_tr_toad_wart', 1), ('zutat_a_salbenfett', 1)], 9),
    ('oil_holy', 'Holy Water of Praios', 'Blessed water. The dead burn where it touches them.', [('race', 'Untoter', [('dmg', 2, 1, 'magic', 'Heal_Impact')])], [('zutat_a_quellwasser', 2), ('zutat_s_blattgold', 1)], 9),
    ('oil_thunder', 'Thunder Salts', 'Crushed gemstone and charcoal. Each blow cracks like lightning.', [('p', 100, [('dmg', 0, 1, 'magic', 'Lightning')])], [('zutat_s_edelsteine', 1), ('zutat_s_kohle', 2)], 12),
]
# no spoilers (review 1 Nov): oils whose ingredients come from later monsters are sold only where those monsters are already behind you
OIL_SELLERS = {'oil_venom': ALCH[2:], 'oil_frailty': ALCH[2:]}
for key, nm, desc, hit, ingr, diff in OILS:
    desc = DESC_R.get(key, desc)
    iid = f'arm_{key}'; NAMES[iid] = nm
    hit_name = m.hit_script(f'arm_{key}', hit)[len('on:Hit:'):]
    lim_hit, lim_add = f'Weapon_arm{key.replace("_", "")}', f'Weapon_add_arm{key.replace("_", "")}'
    lines = procs_text(hit, m.se_names)
    limited(lim_hit, 'Hit', 'Entity', hit_name, nm, '; '.join(lines))
    add_name = action_script(f'item_on_scripts.xml_add_arm{key.replace("_", "")}',
                             lambda b, lh=lim_hit: [b.action(f'AttachActionScript limitedScriptID="{lh}" charge="10" targetEntity="AimedEntity" actionSelection="script"; ')])
    limited(lim_add, 'Use', 'Item', add_name, nm, '; '.join(lines))
    m.template('Item', 'crafted_a_waffenbalsam', iid, nm, desc + '\\n\\nCoats a weapon for 10 hits:\\n' + '\\n'.join(lines),
               ScriptOverride='can:Use:can_use_charged_item.xml', LimitedScript=f'{lim_add}:-1', Value=D(2), IconBrush=icon(key, 'icons/alchimie_item_waffenbalsam', 'amazing'))
    recipe(key, 'Item', iid, nm, 'TaAlchimie', diff, [('Item', i, n) for i, n in ingr], OIL_SELLERS.get(key, ALCH), 6, batch=3, preview='10 hits: ' + '; '.join(lines))
    catalogue.append(('Oil', nm, '; '.join(lines), f'Alchemy {diff}, makes 3'))

# ======================= traps =======================
VICTIM_HURT = lambda f, n, t, fx: f'Hurt who="ActingEntity" fixedDamage="{f}" dice="6" diceAmount="{n}" effect="{fx}" damageType="{t}" {ACT}'
VICTIM_ST = lambda sid: f'SetStatusEffect who="ActingEntity" id="{sid}" {ACT}'
TRAPS = [  # key, name, desc, actions, ingredients, skill, diff, sellers
    ('trap_frost', 'Frost Snare', 'A snare of crab-shell and sinew that freezes what it catches.', [VICTIM_HURT(2, 1, 'magic', 'Corpofrigo_Impact'), VICTIM_ST('corpofrigo')],
     [('arm_tr_crab_plate', 1), ('zutat_b_sehnen', 1), ('zutat_s_lederbaender', 1)], 'TaBogenbau', 8, HUNTERS[1:]),
    ('trap_web', 'Spider-silk Web', 'Sticky silk that drops a foe and saps their strength.', [VICTIM_ST('overthrown'), VICTIM_ST('ArmFrailty')],
     [('seidendruese', 2), ('zutat_b_sehnen', 1)], 'TaBogenbau', 9, HUNTERS[1:]),
    ('trap_venom', 'Venom Spikes', 'Spikes smeared with scorpion venom.', [VICTIM_HURT(0, 1, 'physical', 'Gift_Impact'), VICTIM_ST('ArmVenom')],
     [('arm_tr_scorpion_sting', 1), ('zutat_b_metallteile', 1)], 'TaSchmieden', 9, MUROLOSH),
    ('trap_thunder', 'Thunder Mine', 'A gemstone primed with a spark. It goes off with a crack of thunder.', [VICTIM_HURT(0, 2, 'magic', 'Lightning'), VICTIM_ST('stun')],
     [('zutat_s_edelsteine', 1), ('zutat_b_metallteile', 1), ('zutat_s_kohle', 2)], 'TaSchmieden', 10, SMITHS),
    ('trap_hex', 'Hexing Glyph', 'A rune drawn in gold leaf. Whoever steps on it is cursed and terrified.', [VICTIM_HURT(0, 1, 'magic', 'Kulminatio_Impact'), VICTIM_ST('ArmHexed'), VICTIM_ST('ArmShaken')],
     [('zutat_s_blattgold', 2), ('zutat_s_edelsteine', 1)], 'TaAlchimie', 10, MAGE),
    ('trap_wyrmfire', 'Wyrmfire Mine', 'Dragon blood and tinder in an iron shell. Devastating.', [VICTIM_HURT(4, 2, 'fire', 'Ignisphaero_Impact'), VICTIM_ST('burning')],
     [('zutat_a_drachenblut', 1), ('zutat_b_zunderschwamm', 2), ('zutat_b_metallteile', 1)], 'TaSchmieden', 12, MUROLOSH),
]
tcols = [c[1] for c in m.s.execute('pragma table_info(_Template_Trap)')]
for key, nm, desc, acts, ingr, skill, diff, sellers in TRAPS:
    desc = DESC_R.get(key, desc)
    iid, tid = f'arm_{key}', f'arm_{key}_placed'; NAMES[iid] = nm
    sname = action_script(f'arm_{key}.xml', lambda b, a=acts: [b.action(''.join(a))])
    trow = dict(m.s.execute("select * from _Template_Trap where Id='trap_baerenfalle_crafted'").fetchone())
    trow.update(Id=tid, LookAtText=f'lookat_{tid}', Name=f'name_{tid}', InfoIdentified=f'infoid_{tid}', ScriptOverride=f'on:TriggerTrap:{sname}', IconBrush=f'icons/arm_{key}')
    m.static += [f"DELETE FROM _Template_Trap WHERE Id={lit(tid)};", insert('_Template_Trap', trow)]
    m.undo_static.append(f"DELETE FROM _Template_Trap WHERE Id={lit(tid)};")
    for k in ('lookat', 'name', 'infoid'): m.text(f'{k}_{tid}', nm)
    eff = re.sub(r'\s+', ' ', ', '.join(x for x in (
        ('damage' if 'Hurt' in a else m.se_names.get(re.search(r'id="(\w+)"', a).group(1), re.search(r'id="(\w+)"', a).group(1))) for a in acts)))
    m.template('Item', 'trap_baerenfalle', iid, nm, desc + f'\\n\\nTrap (Set traps). Triggers: {eff}.', TrapId=f'Trap/{tid}', Value=D(3),
               IconBrush=icon(key, 'icons/trap_baerenfalle', 'amazing'))
    recipe(key, 'Item', iid, nm, skill, diff, [('Item', i, n) for i, n in ingr], sellers, 6, batch=3, preview=f'Trap: {eff}')
    catalogue.append(('Trap', nm, eff, f'{SKILL[skill]} {diff}, makes 3'))

# ======================= wands (5 charges, aimed at an enemy) =======================
WANDS = [  # key, name, desc, procs on target, ingredients, diff, place
    ('wand_ember', 'Wand of Embers', 'A charred wand tipped with a firefly sac.', [('dmg', 0, 2, 'fire', 'Ignisphaero_Impact'), ('st', 'burning')],
     [('arm_tr_firefly_sac', 2), ('zutat_s_edelsteine', 1)], 10, ('chest', 'loc08_gruft_sarg_tagebuch_04', 'dungeon08_gruft_01')),
    ('wand_frost', 'Wand of Rime', 'A wand of white wood capped with crab shell.', [('dmg', 2, 1, 'magic', 'Corpofrigo_Impact'), ('st', 'corpofrigo')],
     [('arm_tr_crab_plate', 2), ('zutat_s_edelsteine', 1)], 10, ('chest', 'loc04_steinknopf_chest', 'location04')),
    ('wand_thunder', 'Thunder Rod', 'An iron rod wrapped in copper wire. It crackles.', [('dmg', 0, 2, 'magic', 'Lightning'), ('p', 50, [('st', 'stun')])],
     [('zutat_s_edelsteine', 2), ('zutat_b_metallteile', 1)], 12, ('chest', 'loc10_chest_zwergenskelett', 'location10')),
    ('wand_wither', 'Wand of Withering', 'Black bone tipped with crypt-chitin. It drains strength and will.', [('dmg', 0, 1, 'magic', 'Kulminatio_Impact'), ('st', 'ArmHexed'), ('st', 'ArmFrailty')],
     [('arm_tr_louse_carapace', 2), ('zutat_s_edelsteine', 1)], 12, ('chest', 'skelett_tot_sitzend_dun08_haendler', 'dungeon08_haendler')),
]
for key, nm, desc, procs, ingr, diff, place in WANDS:
    desc = DESC_R.get(key, desc)
    iid = f'arm_{key}'; NAMES[iid] = nm; lid = f'Item_arm{key.replace("_", "")}'
    sname = action_script(f'arm_{key}.xml', lambda b, p=procs: [b.if_('IsInRange entity="ActingEntity" target="AimedEntity" range="49"; ', lambda: build_procs(b, p))])
    lines = ', '.join(procs_text([('p', 100, procs)], m.se_names)).replace('On hit: ', '')
    limited(lid, 'Use', 'Enemy', sname, nm, lines)
    m.template('Item', 'LissoksSichel-Fulminictus', iid, nm, desc + f'\\n\\n5 charges. Aim at an enemy: {lines}.', LimitedScript=f'{lid}:5;', Value=D(5),
               IconBrush=icon(key, 'icons/weapon_magierstab', 'superrare'))
    m.place('Item', iid, *place)
    recipe(key, 'Item', iid, nm, 'TaBogenbau', diff, [('Item', i, n) for i, n in ingr], MAGE, 12, preview=f'5 charges: {lines}')   # wands: woodwork
    catalogue.append(('Wand', nm, lines, f'Arcane lore {diff}; one found in {place[2]}'))

# ======================= scrolls (consumable, potion pattern) =======================
SCROLLS = [('scroll_haste', 'Scroll of Haste', 'ArmScrollHaste'), ('scroll_shadow', 'Scroll of Shadow Veil', 'ArmScrollShadow'),
           ('scroll_iron', 'Scroll of Iron Skin', 'ArmScrollIron'), ('scroll_trance', 'Scroll of Battle Trance', 'ArmScrollTrance'),
           ('scroll_mend', 'Scroll of Mending', 'ArmScrollMend')]
for key, nm, sid in SCROLLS:
    iid = f'arm_{key}'; NAMES[iid] = nm
    sname = action_script(f'item_on_scripts.xml_arm{key.replace("_", "")}', lambda b, s=sid: [b.action(f'SetStatusEffect who="ActingEntity" id="{s}" {ACT}')])
    desc = m.locale[f'{sid}_long']
    m.template('Item', 'crafted_a_zielwasser', iid, nm, f'Read it aloud and the runes burn away.\\n\\n{desc} Lasts {"30 s" if sid == "ArmScrollMend" else "60 s"}.',
               ScriptOverride=f'on:Use:{sname}', Value=D(3), IconBrush=icon(key, 'icons/recipe_kriegspfeil', 'amazing'))
    recipe(key, 'Item', iid, nm, 'TaAlchimie', 8, [('Item', 'zutat_s_blattgold', 1), ('Item', 'zutat_a_alkohol', 1)], MAGE, 8, batch=2, preview=desc)
    for o, l in MAGE: m.place('Item', iid, 'npc', o, l, stack=3)
    catalogue.append(('Scroll', nm, desc, 'Arcane lore 8, makes 2; 3 sold by the Tallon magic trainer'))

# ======================= Attributo, made dependable (player, 3 Nov) =======================
# The complaint: even at the end of the game Attributo rolls a different bonus every cast, so you recast for a good roll every 5 minutes.
# The Attributo lab (3 Nov, player-tested, docs/ENGINE_REFERENCE.md) found the fix: the spell rolls against Life max (ZaP1-3 = 'LEmax')
# instead of KL/CH/attribute, so the dice never eat spell points. Every cast lands at its best for the spell value (+value/3 +1), and
# raising the value raises it. Lasts an hour. ZaVal3 (base) is ignored by the engine; the slider, Area targets and status hooks failed.
for _id, _d in m.s.execute("select Id, Description from _Template_Zauber where Id like 'Attributo%'").fetchall():
    m.edit_vanilla('Zauber', _id, ZaP1='LEmax', ZaP2='LEmax', ZaP3='LEmax', ZaDuration=3600.0)
    _t = (m.l.execute('select LocaText from _Locale where LocaId=?', (_d,)).fetchone() or [None])[0]
    if _t:
        _n = (_t.replace('+SP*/3+1, min. 1', '+SP/3+1, always at full strength for the spell value (no bad rolls)')
                .replace('Spell Duration: 300 secs', 'Spell Duration: 1 hour'))
        if _n != _t: m.vanilla_text(_d, _n)

# ======================= Focus Talismans: the Circle (player, 3 Nov: a party-wide Attributo) =======================
# One quick-slot charm per Attributo. The bearer casts the real spell on every party member, at the bearer's own spell
# value (so the learning points count), paying the astral points of each cast. Proven (lab): CastSpell from an item works only for a
# bearer who knows the spell; several CastSpells in one script replace each other, so a short status casts them one by one (below).
# Potion-base items with CanDestroy 0 are not used up, so there is no give-it-back line any more (it duplicated them).
FOCUS = [('MU', 'Courage'), ('KL', 'Cleverness'), ('IN', 'Intuition'), ('CH', 'Charisma'), ('FF', 'Dexterity'), ('GE', 'Agility'),
         ('KO', 'Constitution'), ('KK', 'Strength')]
# RunActionScriptInRadius + CastSpell did nothing (player, 3 Nov): the bearer is not ActingEntity inside the radius script. The engine
# has no "every companion" token, so the charm names them: the Hero, then each companion who is in the party (vanilla IsPartyMember names).
COMPANIONS = ['Rhulana', 'Dranor_PC', 'Kladdis_Schladromir', 'Forgrimm_Sohn_des_Ferolax', 'pc_gwendala', 'pc_jost', 'pc_nasreddin',
              'pc_traldar', 'pc_ancoron', 'pc_auralia']
# Several CastSpells in one script replace each other (player, 3 Nov: only Rhulana, the last, got it; like a click without Ctrl). So the
# charm puts a short "Circle" status on the bearer whose trigger casts on one companion, waits for the cast, then the next one.
# Status scripts: every If needs an Else (T9 crash). who="StatusEffectEntity" CRASHED (token not set, tokenmanager.cc 222);
# vanilla status scripts name nobody and act on the bearer, so the cast has no who. PROVEN (player, 3 Nov): one use buffs the party.
CIRCLE_GAP = 4   # seconds per cast (Attributo's animation is about 2-3 s)
def circle_status(at, an):
    sid = f'ArmCircle{at}'
    A = 'actionSelection="script"; '
    tr = Block(f'remastered/se/{sid}/trigger')
    cast = lambda who: [tr.action(f'CastSpell spellId="Attributo{at}" target="{who}" {A}'
                                  f'WaitAction duration="{CIRCLE_GAP}" permanent="false" {A}')]
    skip = lambda: [tr.action(f'WaitAction duration="0.1" permanent="false" {A}')]
    kids = cast('Hero') + [tr.if_(f'IsPartyMember who="{c}"; ', lambda c=c: cast(c), build_else=skip) for c in COMPANIONS]
    kids.append(tr.action(f'WaitAction duration="0.1" permanent="false" {A}'))
    tr.begin(kids)
    m.static.append(f'-- status effect {sid}'); m.emit_block(tr)
    Z = bytes(16); sg = U(m.ns, 'se', sid)
    m.static.append(insert('_Scripts_StatusEffectScripts', dict(Guid=sg, Id=sid, Name='', StatusEffectOnStartRef=Z, StatusEffectOnStartBlock=Z,
        StatusEffectOnTriggerRef=tr.ref, StatusEffectOnStopRef=Z, StatusEffectOnTriggerBlock=tr.guid, StatusEffectOnStopBlock=Z,
        StatusEffectCategories='', StatusEffectTexture='', StatusEffectStackable=0, StatusEffectPower=1)))
    m.static.append(insert('_Template_Statuseffects', dict(Id=sid, State_Effect='', State_Hardpoint='', State_Sound='',
        State_Texture='textures:icons/status_fx_good_plus.dds', State_Categories='buff;good', Name=f'{sid}_name',
        ShortDescription=f'{sid}_short', LongDescription=f'{sid}_long', State_Immunity='')))
    m.undo_static += [f"DELETE FROM _Scripts_StatusEffectScripts WHERE Guid={lit(sg)};", f"DELETE FROM _Template_Statuseffects WHERE Id={lit(sid)};"]
    m.locale[f'{sid}_name'] = m.locale[f'{sid}_short'] = f'Circle of {an}'
    m.locale[f'{sid}_long'] = f'Casting Attributo ({an}) on each companion in turn.'
    m.se_names[sid] = f'Circle of {an}'; m.new_guids.append(sg)
    return sid
for _at, _an in FOCUS:
    _cs = circle_status(_at, _an)
    _sname = action_script(f'item_on_scripts.xml_armfocus{_at.lower()}',
                           lambda b, cs=_cs: [b.action(f'SetStatusEffect who="ActingEntity" id="{cs}" {ACT}')])
    _iid = f'arm_focus_{_at.lower()}'; _nm = f'Focus Talisman: {_an}'; NAMES[_iid] = _nm
    m.template('Item', 'crafted_a_zielwasser', _iid, _nm,   # a potion base can be used from a quick slot
               f"A charm carved with the Attributo rune for {_an.lower()}, worn by the circle's caster. Through it one spell reaches the whole company.\\n\\n"
               f"Use it from a quick slot: the bearer casts Attributo ({_an}) on every companion in the party, at the bearer's "
               f"own spell value, paying the astral points of each cast. Only for a bearer who knows the spell. Never used up.",
               ScriptOverride=f'on:Use:{_sname}', CanDestroy=0, MaxStackCount=1, QuestId='NONE', Robable=0, Value=D(12),
               IconBrush=icon(f'focus_{_at.lower()}', 'icons/magic_amulett_01', 'superrare'))
    for _o, _l in [('npc_gen_magierin_typ1_loc02_trainer_praios_magie', 'location02_praios')] + MAGE:
        m.place('Item', _iid, 'npc', _o, _l, tag='focus')
    catalogue.append(('Talisman', _nm, f'the bearer casts Attributo ({_an}) on the whole party nearby', 'sold by the magic trainers in Ferdok and Tallon'))

# archetype_EL_KA_M/W carry 'SpellQuickSlot=FlimFlamFunkel=1' without the 'Game::' class prefix: the game asserts
# (Factory::ClassExists(quickSlotTokens[0]), quickslotproperty.cc 250) when the character is made. Any such token gets its prefix back.
for _t in ('PC_CharWizard', 'PC'):
    for _r in m.s.execute(f"select Id, QuickSlotSetting from _Template_{_t}").fetchall():
        _toks = (_r['QuickSlotSetting'] or '').split(';')
        _fixed = [x if (not x or x == 'empty' or x.startswith('Game::')) else 'Game::' + x for x in _toks]
        if _fixed != _toks: m.edit_vanilla(_t, _r['Id'], QuickSlotSetting=';'.join(_fixed))

# ======================= skill-check weapons (talent roll on hit) =======================
def probe(attr, diff, kids): return ('raw_if', f'Probe who="ActingEntity" difficulty="{diff}" attribute="{attr}" showProbe="true"; ', kids)
SKILLW = [  # key, base, name, desc, talent, label, kids, stats, place
    ('sk_phex_gambit', 'Langdolch', "Phex's Gambit", 'A thief\'s dirk. Feel for the gap, then strike.', 'Taschendiebstahl', 'Pickpocket',
     [('dmg', 2, 1, 'physical', ''), ('st', 'ArmDazed')], dict(WpW6plus=5, WpATmod=1), (TALLON_THIEF[0], TALLON_THIEF[1], 'npc')),
    ('sk_scholar_edge', 'Magierdegen', "Scholar's Edge", 'A mage\'s epee etched with formulae. Knowledge cuts.', 'Magiekunde', 'Arcane lore',
     [('asp', 3), ('dmg', 0, 1, 'magic', 'Kulminatio_Impact')], dict(WpW6plus=5), ('npc_magiertrainer_loc08_trainer_magie', 'location08', 'npc')),
    ('sk_huntmaster', 'Langbogen', "Huntmaster's Bow", 'A heavy longbow for a hunter who knows where to aim.', 'Tierkunde', 'Animal lore',
     [('dmg', 2, 1, 'physical', '')], dict(WpW6plus=4), ('Jaeger_Kauzenstein_loc08_jaeger', 'location08', 'npc')),
    ('sk_forgemaster', 'Kriegshammer', "Forgemaster's Maul", 'A smith\'s two-handed maul. A craftsman knows where metal breaks.', 'Schmieden', 'Smithing',
     [('st', 'stun'), ('dmg', 0, 1, 'physical', 'Niederwerfen')], dict(WpW6plus=4), ('Zwerg_Handwerker_loc09_schmied', 'location09', 'npc')),
]
for key, base, nm, desc, talent, label, kids, stats, (o, l, kind) in SKILLW:
    iid = f'arm_{key}'; NAMES[iid] = nm
    b = Block(f'{m.ns}/hit/arm_{key}')
    b.begin([b.if_(f'Probe who="ActingEntity" difficulty="4" attribute="{talent}" showProbe="true"; ', lambda k=kids, bb=b: build_procs(bb, k))])
    sname = f'weapon_on_scripts.xml_arm_{key}'
    m.static.append(f'-- on-hit {sname}'); m.emit_block(b)
    m.static.append(insert('_Scripts_ActionScripts', dict(ScriptName=sname, StatementRef=b.ref, StatementBlock=b.guid)))
    m.undo_static.append(f"DELETE FROM _Scripts_ActionScripts WHERE ScriptName={lit(sname)};")
    eff = ', '.join(procs_text([('p', 100, kids)], m.se_names)).replace('On hit: ', '')
    m.template('Weapon', base, iid, nm, desc + f'\\n\\nOn hit, a {label} check (+4): if it succeeds, {eff}.', ScriptOverride=f'on:Hit:{sname}', IsMagical=1,
               Value=D(30), PermanentEffect='', IconBrush=icon(key, m.s.execute('select IconBrush from _Template_Weapon where Id=?', (base,)).fetchone()[0], 'superrare'), **stats)
    m.place('Weapon', iid, kind, o, l)
    catalogue.append(('Skill weapon', nm, f'{label} check on hit: {eff}', f'sold by `{o}`'))

# ======================= living-weapon chains (each stage consumes the previous one) =======================
m.template('Weapon', 'Amazonensaebel', 'arm_ch_pridefang', 'Pridefang', "A Kurkum lioncub saber reforged with Kosh steel for an Amazon who has led her first charge. The lion on the guard has grown teeth.\\n\\n"
           "15% on hit: Sundered Guard\\n8% on hit: wielder gains Lion's Roar", ScriptOverride=m.hit_script('arm_ch_pridefang', [('p', 15, [('st', 'ArmSundered')]),
           ('p', 8, [('buff', 'ArmLionroar')])]), WpW6plus=7, WpATmod=1, IsMagical=1, Value=D(12), PermanentEffect='', IconBrush=icon('ch_pridefang', 'icons/weapon_amazonensaebel', 'superrare', (255, 225, 120)))
NAMES.update({'arm_ch_pridefang': 'Pridefang', 'arm_a_lioncub': 'Lioncub Saber', 'arm_s_rondra_reprimand': "Rondra's Reprimand", 'arm_a_felling_maul': 'Felling Maul',
              'arm_s_mountain_patience': "Mountain's Patience", 'arm_w_whisperwind': 'Whisperwind', 'arm_s_nightsong': 'Nightsong', 'arm_d_twinfang': 'Twinfang',
              'arm_d_black_widow': 'Black Widow'})
CHAINS = [  # key, consumes, result, materials, skill, diff, sellers, price, who
    ('chain_pridefang', 'arm_a_lioncub', 'arm_ch_pridefang', [('zutat_s_stahlkoscher', 2)], 'TaSchmieden', 10, [SMITHS[1]], 10, 'Rhulana 1/3'),
    ('chain_reprimand', 'arm_ch_pridefang', 'arm_s_rondra_reprimand', [('zutat_s_stahlzwergen', 2), ('zutat_s_blattgold', 2)], 'TaSchmieden', 12, MUROLOSH, 15, 'Rhulana 2/3 (Fang of the Lioness is found)'),
    ('chain_patience', 'arm_a_felling_maul', 'arm_s_mountain_patience', [('zutat_s_stahlzwergen', 2)], 'TaSchmieden', 12, MUROLOSH, 15, 'Forgrimm (Last Oath is found)'),
    ('chain_nightsong', 'arm_w_whisperwind', 'arm_s_nightsong', [('zutat_b_elfenholz', 1), ('zutat_b_verbesserte_sehne', 1)], 'TaBogenbau', 12, [HUNTERS[2]], 15, 'Gwendala (Sala Mandra is found)'),
    ('chain_widow', 'arm_d_twinfang', 'arm_d_black_widow', [('arm_tr_spider_eye', 2)], 'TaSchmieden', 11, [SMITHS[1]], 12, 'Arcane Thief'),
]
for key, cons, res, mats, skill, diff, sellers, price, who in CHAINS:
    recipe(key, 'Weapon', res, NAMES[res], skill, diff, [('Weapon', cons, 1)] + [('Item', i, n) for i, n in mats], sellers, price,
           preview=f'Upgrades {NAMES[cons]} into {NAMES[res]}.')
    catalogue.append(('Chain', f'{NAMES[cons]} -> {NAMES[res]}', who, f'{SKILL[skill]} {diff}'))

# ======================= set bonuses (possession check with Else; proven in Phase 0b B11) =======================
SETS = [  # pe id, jewelry it is added to, required piece (type, id), bonus, fallback, label
    ('PeArmSetNightfox', 'arm_n_signet', ('Armor', 'arm_n_hood'), 'AW +1 TaSchleichen +3 TaSchloesser +2', 'TaSchleichen +1', 'Nightfox set: with the Nightfox Hood, Dodge +1, Sneak +3, Open locks +2'),
    ('PeArmSetKurkum', 'arm_j_amazon_queen', ('Shield', 'arm_l_kurkum_aegis'), 'MU +1 CH +1 LEmax +5', 'CH +1', 'Kurkum set: with the Kurkum Aegis, Courage +1, Charisma +1, LE +5'),
    ('PeArmSetForge', 'arm_j_mountain_king', ('Armor', 'arm_fx_plate'), 'LEmax +10 KO +1', 'TaSchmieden +1', "Mountain King set: with Ferolax's Forge-Plate, LE +10, Constitution +1"),
    ('PeArmSetWyrm', 'arm_a_umbracor_splinter', ('Armor', 'arm_w_scale_cuirass'), 'KK +1 MU +1', 'TaTierkunde +1', 'Wyrm set: with the Wyrmscale Cuirass, Strength/Courage +1'),
]
Z = bytes(16)
for pid, jid, (rt, rid), bonus, fallback, label in SETS:
    st = Block(f'remastered/se/{pid}/start')
    st.begin([st.if_(f'HasItem owner="PlayerParty" templateId="{rid}" category="{rt}" amount="1"; ',
                     lambda b=st, x=bonus: [b.action(f'ModifyAttribute modifier="{x}" actionSelection="script"; ')],
                     build_else=lambda b=st, x=fallback: [b.action(f'ModifyAttribute modifier="{x}" actionSelection="script"; ')])])
    tr = Block(f'remastered/se/{pid}/trigger'); tr.begin([tr.action('WaitAction duration="1" permanent="true" actionSelection="script"; ')])
    m.emit_block(st); m.emit_block(tr)
    sg = U('remastered', 'se', pid)
    m.static.append(insert('_Scripts_StatusEffectScripts', dict(Guid=sg, Id=pid, Name='', StatusEffectOnStartRef=st.ref, StatusEffectOnStartBlock=st.guid,
        StatusEffectOnTriggerRef=tr.ref, StatusEffectOnStopRef=Z, StatusEffectOnTriggerBlock=tr.guid, StatusEffectOnStopBlock=Z,
        StatusEffectCategories='', StatusEffectTexture='', StatusEffectStackable=1, StatusEffectPower=1)))
    m.static.append(insert('_Template_Statuseffects', dict(Id=pid, State_Effect='', State_Hardpoint='', State_Sound='', State_Texture='textures:icons/status_fx_good_jewel.dds',
        State_Categories='permanentEffect', Name=f'{pid}_name', ShortDescription=f'{pid}_name', LongDescription=f'{pid}_name', State_Immunity='')))
    m.undo_static += [f"DELETE FROM _Scripts_StatusEffectScripts WHERE Guid={lit(sg)};", f"DELETE FROM _Template_Statuseffects WHERE Id={lit(pid)};"]
    m.text(f'{pid}_name', label); m.new_guids.append(sg)
    # append to the Armory item (template + placed copies); undo removes exactly what was added
    for t in ('_Template_Jewelry',):
        m.static.append(f"UPDATE {t} SET PermanentEffect=PermanentEffect||';{pid}' WHERE Id={lit(jid)} AND PermanentEffect NOT LIKE '%{pid}%';")
        m.undo_static.append(f"UPDATE {t} SET PermanentEffect=REPLACE(PermanentEffect,';{pid}','') WHERE Id={lit(jid)};")
    m.game.append(f"UPDATE _Instance_Jewelry SET PermanentEffect=PermanentEffect||';{pid}' WHERE Id={lit(jid)} AND PermanentEffect NOT LIKE '%{pid}%';")
    m.undo_game.append(f"UPDATE _Instance_Jewelry SET PermanentEffect=REPLACE(PermanentEffect,';{pid}','') WHERE Id={lit(jid)};")
    catalogue.append(('Set bonus', label, f'otherwise {mods_text(fallback)}', f'on {jid} (checked when equipped)'))

# ======================= gathering kit (herbs and animal parts without a specialist) =======================
HERBS = [('alchimistin_loc01', 'location01'), ('Dorfbewohnerin_loc02_haendler_praios_kraeuter', 'location02_praios'), ('Haendlerin_1_loc08_haendler_kraeuter', 'location08')]
GATHER = [  # type, key, base, name, desc, mods, sellers, value D
    ('Armor', 'g_gloves', 'handschuhe_horasischer_einbrecher', "Gatherer's Gloves", 'Thin leather gloves stained green and red: herbs and hides.', 'TaPflanzenkunde +2 TaTierkunde +2',
     [('Dorfbewohner04_loc02_haendler_praios_gemischt', 'location02_praios')], 5),
    ('Jewelry', 'g_green_thumb', 'Silberring', 'Ring of the Green Thumb', 'A ring of twisted vine silver. Plants seem to lean towards it.', 'TaPflanzenkunde +3',
     [('Peraine_Priesterin_01_loc02_haendler_graf_kraeuter', 'location02_grafenstadt')], 10),
    ('Jewelry', 'g_hunter_totem', 'Silberkette', "Hunter's Totem", 'A carved bone totem: the hunter, the herb-woman and the wanderer.', 'TaTierkunde +3 TaPflanzenkunde +2',
     [('Jaeger_Kauzenstein_loc08_jaeger', 'location08')], 15),
]
for typ, key, base, nm, desc, mods, sellers, price in GATHER:
    iid = f'arm_{key}'; NAMES[iid] = nm
    pe = m.status('PeArm' + ''.join(w.capitalize() for w in key.split('_')), mods_text(mods), mods_text(mods), start=mods)
    extra = dict(IsMagical=1) if typ == 'Weapon' else {}
    m.template(typ, base, iid, nm, desc + '\\n\\n' + mods_text(mods), PermanentEffect=pe, Value=D(price),
               IconBrush=icon(key, m.s.execute(f'select IconBrush from _Template_{typ} where Id=?', (base,)).fetchone()[0], 'regular' if price < 10 else 'amazing'), **extra)
    for o, l in sellers: m.place(typ, iid, 'npc', o, l)
    catalogue.append(('Gathering', nm, mods_text(mods), ', '.join(f'`{o}`' for o, _ in sellers)))
# Tools are NOT equipped (review 1 Nov): like the vanilla furrier's knife and herb sickle, they sit on the hotbar and are used on the
# corpse or plant (UseTalent + TaBonus), so nobody has to swap weapons while exploring.
TOOLS = [  # key, vanilla tool base, name, desc, talent, bonus, sellers, price, (upgrade of, materials, skill, diff, recipe sellers, recipe price)
    ('r_skinner', 'special_kuerschnermesser', "Huntress' Skinning Knife", 'Owlstone keeps it sharp enough to split a hair.', 'TaTierkunde', 2,
     [('Jaeger_Kauzenstein', 'location01'), ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')], 9, None),
    ('g_sickle', 'special_kraeutersichel', "Herbalist's Sickle", 'A small curved blade for cutting herbs at the root, the way Peraine teaches.', 'TaPflanzenkunde', 2, HERBS, 4, None),
    ('g_master_furrier', 'special_kuerschnermesser', "Master Furrier's Knife", "A furrier's knife of fine Kosh steel. Every pelt, every claw comes off whole.", 'TaTierkunde', 3,
     [('Jaeger_Kauzenstein_loc08_jaeger', 'location08')], 12, None),
    ('g_golden_sickle', 'special_kraeutersichel', "Druid's Golden Sickle", 'A golden sickle from the Moorbridge druids. It never wilts what it cuts.', 'TaPflanzenkunde', 3,
     [('Dorfbewohnerin01_loc04', 'location04')], 14, None),
    ('g_grand_furrier', 'special_kuerschnermesser', "Grandmaster Furrier's Knife", 'Dwarven steel and a tatzelwurm fang. No beast is too tough to skin.', 'TaTierkunde', 4, [], 10,
     ('arm_g_master_furrier', [('arm_tr_tatzel_fang', 1), ('zutat_s_stahlzwergen', 1)], 'TaSchmieden', 12, MUROLOSH, 15)),
    ('g_harvest_sickle', 'special_kraeutersichel', "Sickle of Peraine's Harvest", 'Blessed gold and a living ember: every herb yields more.', 'TaPflanzenkunde', 4, [], 10,
     ('arm_g_golden_sickle', [('zutat_s_blattgold', 2), ('zutat_s_edelsteine', 1), ('arm_tr_firefly_sac', 1)], 'TaAlchimie', 12, [HERBS[2]], 15)),
]
TALENT_NAME = {'TaTierkunde': 'Animal Lore', 'TaPflanzenkunde': 'Plant Lore'}
for key, base, nm, desc, ta, bonus, sellers, price, up in TOOLS:
    desc = DESC_R.get(key, desc)
    iid = f'arm_{key}'; NAMES[iid] = nm
    use = f"Tool: put it in a quick slot and use it on a {'corpse' if ta == 'TaTierkunde' else 'plant'}: {TALENT_NAME[ta]} +{bonus} for that check. Never needs to be equipped."
    m.template('Item', base, iid, nm, desc + '\\n\\n' + use, UseTalent=ta, TaBonus=bonus, Value=D(price),
               IconBrush=icon(key, m.s.execute('select IconBrush from _Template_Item where Id=?', (base,)).fetchone()[0], 'amazing' if not up else 'superrare'))
    for o, l in sellers: m.place('Item', iid, 'npc', o, l)
    if up:
        cons, mats, skill, diff, rsell, rprice = up
        recipe(key, 'Item', iid, nm, skill, diff, [('Item', cons, 1)] + [('Item', i, n) for i, n in mats], rsell, rprice,
               preview=f'{TALENT_NAME[ta]} +{bonus} (tool). Upgrades {NAMES[cons]}.')
    catalogue.append(('Gathering tool', nm, f'{TALENT_NAME[ta]} +{bonus} (quick-slot tool)', ', '.join(f'`{o}`' for o, _ in sellers) or 'crafted'))

# ======================= surprises: small secret items with jokes and lore =======================
SAY = lambda who, msg: ('raw', f'ShowOverHeadMessage msg="{msg}" who="{who}"; ')
m.status('ArmOmelette', "Rakorium's Omelette", 'Courage +3, Strength +1, Cleverness -1. You feel draconic. You are not.', start='MU +3 KK +1 KL -1', duration=600,
         state_effect='', texture='status_fx_good_drink', categories='buff;good')
TAVERN = ('Wirt_Tradan_Brauerlich', 'dungeon02_taverne_silberkrug')
SURPRISE = [  # type, key, base, name, desc, mods, hit, stats, placement(s), value D
    # ---- companion gifts (review 31 Oct): each companion brings a small personal thing (in their own inventory when they join) ----
    ('Jewelry', 'cg_dranor', 'Silberring', "Dranor's Die-Ring", "A little ivory die on a short silver chain, fixed to a ring so Dranor can never lose it in a game again. He swears it is honest. It rolls a six suspiciously often.", 'TaFeilschen +2 TaTaschendiebstahl +2', [], {}, [('pc', 'pc_dranor', 'location01')], 3),
    ('Jewelry', 'cg_kladdis', 'Silberkette', "Kladdis's Feather of Fortune", "A jay feather Kladdis wears for luck. She has never lost it, and never paid for it.", 'TaBetoeren +3 TaSchleichen +2', [], {}, [('pc', 'pc_kladdis', 'location02_fuhrmannsheim')], 3),
    ('Jewelry', 'cg_traldar', 'Silberkette', "Traldar's Campaign Medal", "From a war nobody in Ferdok remembers. Traldar remembers every name.", 'TaEtikette +3 AUmax +5', [], {}, [('pc', 'pc_traldar', 'dungeon02_residenz')], 3),
    ('Jewelry', 'cg_nasreddin', 'Goldring', "Nasreddin's Ring of a Hundred Prices", "Engraved inside: 'Everything has a price. Mine is higher.'", 'TaFeilschen +3 TaUeberreden +3', [], {}, [('pc', 'pc_nasreddin', 'location02_hafen')], 3),
    ('Jewelry', 'cg_auralia', 'Silberkette', "Auralia's Pocket Alembic", "A thumb-sized glass still on a chain. It bubbles when someone lies nearby.", 'TaAlchimie +3 TaPflanzenkunde +2', [], {}, [('pc', 'pc_auralia', 'location02_grafenstadt')], 3),
    ('Jewelry', 'cg_ancoron', 'Silberkette', "Ancoron's Silver Leaf", "A leaf from the tree his family planted when he was born. It never wilts.", 'AEmax +8 MR +1', [], {}, [('pc', 'pc_ancoron', 'location08')], 4),
    # ---- more lore jokes ----
    ('Jewelry', 'cg_rhulana', 'Silberring', "Kurkum Sister-Ring", "Every Amazon of Kurkum receives one when she swears to the Lioness. Inside, two names: Rhulana, and a second one scratched out until only an 'S' remains. Rhulana will not say whose.", 'TaSaebel +1 TaSelbstbeherrschung +1', [], {}, [('pc', 'pc_rhulana', 'location01')], 3),
    ('Armor', 'x_rk_unmagical_hat', 'hut_kampfmagier', "Rakorium's Unmagical Hat", "Not a speck of magic in it. Rakorium insists that is precisely its power. His second-best hat, he claims, is resting somewhere much further down the road, among the dead.", '', [], {}, [('loot', 'loot_loc01_truhe_baerenhoehle_verschlossen_wasser', 'all')], 0),
    ('Jewelry', 'x_wanted_poster', 'Silberkette', "Your Own Wanted Poster", "1000 ducats, dead or alive. The drawing looks nothing like you, which is exactly why you wear it, folded, over your heart.", 'TaGassenwissen +3 CH -1', [], {}, [('npc', 'Dorfbewohner04_loc02_haendler_praios_gemischt', 'location02_praios')], 2),
    ('Jewelry', 'x_warpaint', 'Silberkette', "Pot of Kurkum Warpaint", "Rhulana's spare warpaint, in a clay pot on a cord. Smells of iron and berries. Etiquette suffers; courage does not.", 'MU +1 TaEtikette -2', [], {}, [('npc', 'Handwerkerin_1_loc08_haendler_handwerk', 'location08')], 4),
    ('Jewelry', 'x_jar_newt', 'Silberkette', "Rakorium's Pet 'Dragon'", "A newt in a jar. Rakorium insists it breathed fire once. It has not breathed fire since. It is, however, very calm.", 'AEmax +3 TaTierkunde +2', [], {}, [('npc', 'Zwerg_Zivilist_02_loc09_gemischtwarenhaendler', 'location09')], 4),
    ('Jewelry', 'x_love_letters', 'Silberkette', "Kladdis's 37th Love Letter", "Unsent, unsigned and wildly misspelled. Addressed to 'you know who you are'. Several people in Ferdok think it is about them.", 'TaBetoeren +2 TaUeberreden +2', [], {}, [('npc', 'Haendler_1_loc02_haendler_hafen_selten_nach_loc05', 'location02_hafen')], 3),
    ('Jewelry', 'x_cyclops_monocle', 'Goldring', "Cyclops Monocle", "A lens the size of a plate, from a cyclops who needed reading glasses. Worn on a finger, you see everything, slightly enlarged.", 'TaSinnenschaerfe +4 GE -1', [], {}, [('chest', 'loc11_chest_feuerbruecke_04', 'location11')], 5),
    ('Jewelry', 'x_lost_braid', 'Silberkette', "Forgrimm's Braid", "The beard braid Forgrimm cut off in shame, as Ardo's bodyguard. Ardo kept it, of course, in his chest of oddities, between the false beard and that shirt.", 'MU +1 TaZwHiebwaffen +1 CH -1', [], {}, [('chest', 'chest_schatztruhe_01_loc02_chest_ee', 'dungeon02_hauptquartier')], 4),
    ('Jewelry', 'x_bredo_tab', 'Silberkette', "Bredo's Unpaid Tab", "A slate covered in chalk tallies of unpaid drinks. Some innkeeper carried it a long way rather than forgive a single one. Your name is at the top. Wearing it makes haggling feel like justice.", 'TaFeilschen +2 TaSelbstbeherrschung +2', [], {}, [('npc', 'bredo_bento_loc03', 'location03')], 1),
    ('Jewelry', 'x_tiny_crown', 'Goldring', "A Very Small Crown", "Knowall insists it is the crown of a prince. It fits on a finger. It does not fit on a frog either.", 'CH +1 TaBetoeren +2', [], {}, [('chest', 'loc03_truhe_alwene', 'location03')], 2),
    ('Weapon', 'x_annoyance', 'Keule', 'Hammer of Mild Annoyance', 'Forged by a smith who hated nobody in particular. It does not hurt much. It is just very, very annoying.',
     '', [('p', 40, [SAY('AimedEntity', 'Ow!')]), ('p', 30, [SAY('AimedEntity', 'Hey!')]), ('p', 15, [SAY('AimedEntity', 'Not the face!')]), ('p', 30, [('st', 'ArmDazed')])],
     dict(WpW6plus=3), [('loot', 'loot_kanalisation02_geheimraum2', 'all')], 1),   # review 1 Nov: the smugglers' stash behind the sewer wall, not on Jischka
    ('Weapon', 'x_tankard', 'Knueppel', 'Ferdok Tankard', 'A pewter tankard of the Silver Jug, reinforced for "discussions". Still half full.',
     '', [('p', 20, [('st', 'stun')]), ('p', 25, [('heal', 2), SAY('ActingEntity', 'Prost!')])], dict(WpW6plus=3), [('npc', *TAVERN)], 5),
    ('Jewelry', 'x_ardo_sock', 'Silberkette', "Ardo's Lucky Sock", "Ardo wore it at the Battle of Silkwiesen and never washed it again. On a string, round your neck. Bold.",
     'MU +2 CH -2', [], {}, [('chest', 'chest_schatztruhe_01_loc02_ardos_truhe', 'dungeon02_hauptquartier')], 0),
    ('Jewelry', 'x_cano_signet', 'Silberring', "Cano's Signet (Probably Stolen)", "Cano sold it to you for one ducat and a wink. The engraving belongs to a Horasian countess. Wear it and people bow to you, "
     "and every merchant doubles his prices for her ladyship. Do not wear it in Vinsalt.",
     'TaEtikette +3 CH +1 TaFeilschen -3', [], {}, [('npc', 'Cuano', 'dungeon02_diebesgilde'), ('npc', 'Cuano_var_nach_loc05', 'dungeon02_diebesgilde')], 1),
    ('Armor', 'x_rakorium_hat', 'hut_kampfmagier', "Rakorium's Second-Best Hat", "Smells of cave mould and dragon theories. Rakorium swears the best one was eaten by a dragon. Of course.",
     'KL +2 IN +1 MU -1 AEmax +5', [], {}, [('chest', 'loc08_gruft_sarg_tagebuch_05', 'dungeon08_gruft_01')], 1),   # Tallon at the earliest (review 31 Oct)
    ('Armor', 'x_retreat_boots', 'schuhe_horasischer_einbrecher', 'Boots of Strategic Retreat', "They have never lost a battle. They have also never stayed for the end of one.",
     'IN +1 AW +1', [], {}, [('chest', 'loc03_truhe_danor', 'location03')], 1),   # player, 2 Nov: plenty of dodge in the game already
    ('Jewelry', 'x_beard_comb', 'Silberring', "Forgrimm's Spare Beard Comb", "A tiny silver comb on a ring. Forgrimm will deny ever owning it. Loudly. With an axe.",
     'KK +1 CH +1', [], {}, [('npc', 'Zwerg_Zivilist_02_loc09_gemischtwarenhaendler', 'location09')], 3),
]
for typ, key, base, nm, desc, mods, hit, stats, places, price in SURPRISE:
    iid = f'arm_{key}'; NAMES[iid] = nm
    over = dict(stats)
    if mods: over['PermanentEffect'] = m.status('PeArm' + ''.join(w.capitalize() for w in key.split('_')), mods_text(mods), mods_text(mods), start=mods)
    elif 'PermanentEffect' in m.s.execute(f'select * from _Template_{typ} limit 1').fetchone().keys(): over['PermanentEffect'] = ''
    if hit: over['ScriptOverride'] = m.hit_script(f'arm_{key}', hit)
    if typ == 'Weapon': over['IsMagical'] = 1
    lines = ([mods_text(mods)] if mods else []) + [x for x in procs_text(hit, m.se_names) if x]
    m.template(typ, base, iid, nm, desc + ('\\n\\n' + '\\n'.join(lines) if lines else ''), Value=D(price),
               IconBrush=icon(key, m.s.execute(f'select IconBrush from _Template_{typ} where Id=?', (base,)).fetchone()[0], 'amazing'), **over)
    for pl in places:
        if pl[0] == 'loot': m.loot(pl[1], typ, iid, mode=pl[2])
        else: m.place(typ, iid, pl[0], pl[1], pl[2])
    catalogue.append(('Surprise', nm, '; '.join(lines) or '-', 'secret'))
# ======================= the bear cave secret (review 1 Nov): robbers tried the bear's den; one of them left a note =======================
# One skeleton in the Avestrue bear cave (its own loot table, the others keep theirs) holds a bear claw, five Einberries and Wenzel's
# last note. The note points to his share, hidden in the seventh chest of the Ferdok thieves' guild obstacle course: a lock tool.
NAMES['arm_x_dead_lockpick'] = "Dead Man's Lockpick"
m.template('Item', 'special_kleinesmesser', 'arm_x_dead_lockpick',   # reusable like the Locksmith knife (the hairpin is used up: CanDestroy 1)
           "Dead Man's Lockpick", "Wenzel's lockpick, bent just so. He never needed it again. "
           "\\n\\nTool: put it in a quick slot and use it on a lock: Pick Locks +3 for that attempt. It never breaks and never needs to be equipped.",
           UseTalent='TaSchloesser', TaBonus=3, MaxStackCount=1, CanDestroy=0, Gew=10, Value=D(4), IconBrush=icon('x_dead_lockpick', 'icons/special_item_haarnadel', 'amazing'))
m.place('Item', 'arm_x_dead_lockpick', 'chest', 'loc02_diebespacour_truhe_07', 'dungeon02_diebesgilde')
_bk = dict(m.s.execute("select * from _Template_Book where Id='loc01_brief_ardo'").fetchone())
_bk.update(Id='arm_x_wenzel_note', Name='name_arm_x_wenzel_note', LookAtText='lookat_arm_x_wenzel_note', BookText='text_arm_x_wenzel_note', QuestId='NONE', Sound='', Value=0)
m.static += ["DELETE FROM _Template_Book WHERE Id='arm_x_wenzel_note';", insert('_Template_Book', _bk)]
m.undo_static.append("DELETE FROM _Template_Book WHERE Id='arm_x_wenzel_note';")
m.text('name_arm_x_wenzel_note', "Wenzel's Last Note"); m.text('lookat_arm_x_wenzel_note', "Wenzel's Last Note")
m.text('text_arm_x_wenzel_note', "Whoever finds this: the Bald One said a cave this deep must hide a treasure. It hid a bear.\\n\\n"
       "My share of the last job is hidden in the city, down where Phex's children learn their trade. Seven is my lucky number. "
       "If the boss asks, the rat-tail sends his regards, and the boss still owes me three ducats.\\n\\n- Wenzel")
_cave = m.loot_tables()['loot_loc01_truhe_baerenhoehle_skelett']; _ce = [e for e in _cave[1].split(';') if e]
_new = ''.join(e + ';' for e in _ce) + 'Item/arm_tr_bear_claw/100/1/1/;Item/zutat_a_spezial_einbeere/100/5/2/;Book/arm_x_wenzel_note/100/1/0/;'
m.static += ["DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_cave_wenzel';",
             insert('_DSA_LootTables', dict(LootTableName='arm_lt_cave_wenzel', LootTableValue=str(len(_ce) + 3), LootTableContent=_new))]
m.undo_static.append("DELETE FROM _DSA_LootTables WHERE LootTableName='arm_lt_cave_wenzel';")
_sk = m.g.execute("select Guid from _Instance_Chest where Id='truhe_kreatur_skelett_01_loc01_baerenhoehle' order by rowid").fetchone()[0]
m.game.append(f"UPDATE _Instance_Chest SET LootTable='arm_lt_cave_wenzel' WHERE Guid={lit(_sk)};")
m.undo_game.append(f"UPDATE _Instance_Chest SET LootTable='loot_loc01_truhe_baerenhoehle_skelett' WHERE Guid={lit(_sk)};")
catalogue.append(('Secret', "Wenzel's Last Note", 'a skeleton in the Avestrue bear cave', "leads to the Dead Man's Lockpick in the Ferdok thieves' guild"))

# Gwendala's Lucky Arrow (3 arrows)
NAMES['arm_x_lucky_arrow'] = "Gwendala's Lucky Arrow"
m.template('Ammo', 'Pfeil', 'arm_x_lucky_arrow', "Gwendala's Lucky Arrow", "She says she has never missed with it. She has, twice. Do not mention it.\\n\\nOn hit: +15 damage\\n50% on hit: Stun",
           ScriptOverride=m.hit_script('arm_x_lucky_arrow', [('p', 100, [('dmg', 15, 0, 'physical', 'Lightning')]), ('p', 50, [('st', 'stun')])]), Value=D(1), IsMagical=1,
           IconBrush=icon('x_lucky_arrow', 'icons/ammo_pfeil_tenobald', 'legendary'))
m.place('Ammo', 'arm_x_lucky_arrow', 'chest', 'loc04_steinknopf_chest', 'location04', stack=3)
# the chickens of Avestrue: skinning (Animal Lore) now yields "dragon eggs" and, very rarely, a golden feather
for key, base, nm, desc, val in (('x_dragon_egg', 'robable_apfel', 'Totally Real Dragon Egg', 'Rakorium insists it is a dragon egg. It is a chicken egg. Rakorium insists.', 1),
                                 ('x_golden_feather', 'zutat_a_giftzahn', 'Golden Feather', 'A feather of pure gold from an Avestrue chicken. Nobody can explain it. The chicken certainly could not.', 200)):
    NAMES[f'arm_{key}'] = nm
    m.template('Item', base, f'arm_{key}', nm, desc, Value=val, Gew=10, IconBrush=icon(key, m.s.execute('select IconBrush from _Template_Item where Id=?', (base,)).fetchone()[0], 'regular'))
CHICKEN_SKIN = 'arm_skin_huhn'
m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(CHICKEN_SKIN)};",
             insert('_DSA_LootTables', dict(LootTableName=CHICKEN_SKIN, LootTableValue='2', LootTableContent='Item/arm_x_dragon_egg/30/1/0/;Item/arm_x_golden_feather/3/1/0/;'))]
m.undo_static.append(f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(CHICKEN_SKIN)};")
for cid in [r[0] for r in m.s.execute("select Id from _Template_Monster where Id like 'Huhn%' and (FurriersLootTable is null or FurriersLootTable='')")]:
    m.edit_vanilla('Monster', cid, FurriersLootTable=CHICKEN_SKIN)
OMELETTE = action_script('item_on_scripts.xml_armomelette', lambda b: [b.action(f'SetStatusEffect who="ActingEntity" id="ArmOmelette" {ACT}')])
NAMES['arm_x_omelette'] = "Rakorium's Omelette"
m.template('Item', 'crafted_a_zielwasser', 'arm_x_omelette', "Rakorium's Omelette", "Made from a genuine dragon egg (chicken). Tastes of courage and slight regret.\\n\\nCourage +3, Strength +1, Cleverness -1 for 10 minutes.",
           ScriptOverride=f'on:Use:{OMELETTE}', Value=D(1), IconBrush=icon('x_omelette', 'icons/alchimie_item_zielwasser', 'regular'))
recipe('x_omelette', 'Item', 'arm_x_omelette', "Rakorium's Omelette", 'TaAlchimie', 3, [('Item', 'arm_x_dragon_egg', 1), ('Item', 'zutat_a_alkohol', 1)], [TAVERN], 1,
       preview='Courage +3, Strength +1, Cleverness -1 for 10 minutes.')
NAMES['arm_x_golden_hen'] = 'Amulet of the Golden Hen'
pe = m.status('PeArmXGoldenHen', 'Dodge +1, Courage +1', 'Dodge +1, Courage +1', start='AW +1 MU +1', state_effect='AttributoGE_State', hardpoint='Skeleton_Root')
m.template('Jewelry', 'Goldkette', 'arm_x_golden_hen', 'Amulet of the Golden Hen', 'The golden feather, set in gold. Enemies hesitate. Somewhere, a chicken clucks approvingly.\\n\\nDodge +1, Courage +1',
           PermanentEffect=pe, Value=D(5), IconBrush=icon('x_golden_hen', 'icons/magic_amulett_02', 'legendary'))

# ======================= The Wyrmward (player, 3 Nov: ONE upgradable armour-enchantment ring, a dragon and cyclops reward) =======================
# Proven (player, 3 Nov): a permanent effect raises the character's own armour zones (RSKo..RSRB), the sheet shows it, and it stacks on
# Armatrutz (its own effect id). One ring that grows, never a set, so the bonus cannot pile up: each stage consumes the one before.
#   I   Ring of Warding     - found in Japhgur's hoard (Tallon, Dragon's Lair)                      armour +1 every zone
#   II  Wyrmward Signet     - Murolosh smith, Smithing 13: ring + dragon blood, dwarven steel, gems  armour +2, MR +1
#   III Ward of the Old Bones - Murolosh smith, Smithing 15: signet + the Cyclops Rune-Bone (Deeps of Gruldur) + gold   armour +3, MR +2, no knockdown
# The Wyrm Scales stay for the heirlooms and reforges (balance audit A3); the horn and the eye-gem stay for Ulfried and the horn talisman.
WARD_ZONES = ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')
_ward = lambda n: ' '.join(f'{z} +{n}' for z in WARD_ZONES)
WARD = [  # id, base, name, tier, armour, extra mods, immunity, flavour, effect line
    ('arm_x_warding', 'Silberring', 'Ring of Warding', 'superrare', 1, '', '',
     "A plain silver band, cold to the touch, with the Armatrutz glyph cut on the inside. Japhgur kept it with his gold: whoever wore it "
     "before him was very hard to kill, and still did not survive.", 'Armour +1 on every zone. Stacks with Armatrutz.'),
    ('arm_x_warding2', 'Goldring', 'Wyrmward Signet', 'legendary', 2, ' MR +1', '',
     "Reforged in Murolosh around a drop of the Purplewyrm's blood. The glyph now runs all the way round the band, and spells slide off "
     "the wearer like rain off scales.", 'Armour +2 on every zone, Magic resistance +1. Stacks with Armatrutz.'),
    ('arm_x_warding3', 'Goldring', 'Ward of the Old Bones', 'mythic', 3, ' MR +2', 'overthrown',
     "The cyclops of Gruldur was old when the dwarves were young, and the rune in its bones was older still. Set into the Wyrmward, it "
     "holds the wearer the way the mountain holds its roots.", 'Armour +3 on every zone, Magic resistance +2, immune to knockdown. Stacks with Armatrutz.'),
]
for _iid, _base, _nm, _tier, _n, _extra, _imm, _fl, _line in WARD:
    NAMES[_iid] = _nm
    _sid = {'arm_x_warding': 'PeArmWarding'}.get(_iid) or 'PeArm' + _iid[4:].replace('_', '').capitalize()   # the tested ring keeps its effect id (saves carry it)
    _pe = m.status(_sid, _line.split('. Stacks')[0], _line, start=_ward(_n) + _extra,
                   state_effect='Armatrutz_State', hardpoint='Damage_Torso', immunity=_imm)
    m.template('Jewelry', _base, _iid, _nm, f'{_fl}\\n\\n{_line}', PermanentEffect=_pe, Value=D({1: 30, 2: 60, 3: 120}[_n]),
               IconBrush=icon(_iid[4:], 'icons/magic_ring_blau' if _n == 1 else 'icons/questitem_goldring', _tier))
m.place('Jewelry', 'arm_x_warding', 'chest', 'loc08a_truhe_japhgur', 'location08_drachenhort')
m.template('Item', 'zutat_s_edelsteine', 'arm_x_cyclops_bone', 'Cyclops Rune-Bone',
           "A finger-bone of the cyclops of Gruldur, as long as a forearm, with one rune carved into it by no hand anyone remembers. "
           "Murolosh smiths will not touch it without a reason.", Value=D(40), IconBrush=icon('x_cyclops_bone', 'icons/zutat_s_edelsteine', 'regular'))
NAMES['arm_x_cyclops_bone'] = 'Cyclops Rune-Bone'
recipe('x_warding2', 'Jewelry', 'arm_x_warding2', 'Wyrmward Signet', 'TaSchmieden', 13,
       [('Jewelry', 'arm_x_warding', 1), ('Item', 'zutat_a_drachenblut', 2), ('Item', 'zutat_s_stahlzwergen', 1), ('Item', 'zutat_s_edelsteine', 1)],
       MUROLOSH, 25, preview='Armour +2 on every zone, Magic resistance +1.')
recipe('x_warding3', 'Jewelry', 'arm_x_warding3', 'Ward of the Old Bones', 'TaSchmieden', 15,
       [('Jewelry', 'arm_x_warding2', 1), ('Item', 'arm_x_cyclops_bone', 1), ('Item', 'zutat_s_blattgold', 2)],
       MUROLOSH, 40, preview='Armour +3 on every zone, Magic resistance +2, immune to knockdown.')
catalogue += [('Ring', 'Ring of Warding', 'armour +1 every zone, stacks with Armatrutz', "Japhgur's hoard"),
              ('Ring', 'Wyrmward Signet', 'armour +2 every zone, MR +1', 'upgrade, Murolosh smith, Smithing 13'),
              ('Ring', 'Ward of the Old Bones', 'armour +3 every zone, MR +2, no knockdown', 'upgrade with the Cyclops Rune-Bone, Smithing 15')]
recipe('x_golden_hen', 'Jewelry', 'arm_x_golden_hen', 'Amulet of the Golden Hen', 'TaBogenbau', 6, [('Item', 'arm_x_golden_feather', 1), ('Item', 'zutat_s_blattgold', 1)], HUNTERS[:1], 3,
       preview='Agility +1, Dodge +2, Courage +1')
catalogue += [('Surprise', "Gwendala's Lucky Arrow", '+15 damage, 50% stun (3 arrows)', 'secret'), ('Surprise', 'Avestrue chickens', 'skinning: dragon egg 30%, golden feather 3%', 'Animal lore'),
              ('Surprise', "Rakorium's Omelette", 'Courage +3, Strength +1, Cleverness -1, 10 min', 'tavern recipe'), ('Surprise', 'Amulet of the Golden Hen', 'Agility +1, Dodge +2, Courage +1', 'Bowcraft 6')]

# ======================= throwing weapons: every plan makes 25, same ingredients (player, 2 Nov) =======================
for _rid, _res in m.s.execute("select r.Id, r.RecipeResult from _Template_Recipe r join _Template_Weapon w on r.RecipeResult like 'Weapon/' || w.Id || '/%' "
                              "where w.TaAttr='TaWurfwaffen' and r.Id not like 'arm_%'").fetchall():
    m.edit_vanilla('Recipe', _rid, RecipeResult=_res.rsplit('/', 1)[0] + '/25')

# throwing weapons weigh a tenth (player, 2 Nov): they are small axes and knives, a stack of 100 must not crush a fighter
for _wid, _gew in m.s.execute("select Id, Gew from _Template_Weapon where TaAttr='TaWurfwaffen' and MaxStackCount >= 100 and Id not like 'arm_%'").fetchall():
    m.edit_vanilla('Weapon', _wid, Gew=max(1, _gew // 10))

# ======================= firefly ember sacs (player, 2 Nov): fireflies cannot be skinned, yet 14 plans need the sac =======================
# small fireflies drop one now and then, the big one always, and the
# herbalists after Ferdok keep a few.
m.loot('loot_feuerfliege_klein', 'Item', 'arm_tr_firefly_sac', mode='all', chance=30, amount=1)
_BIG_FLY = next(n for n in m.loot_tables() if n.startswith('loot_feuerfliege_gro'))   # 'loot_feuerfliege_groß' (cp1252 name)
m.loot(_BIG_FLY, 'Item', 'arm_tr_firefly_sac', mode='all', chance=100, amount=1)
for _npc, _lvl, _n in (('Saphira_Trader', 'location03', 2), ('Dorfbewohnerin01_loc04', 'location04', 2),
                       ('Haendlerin_1_loc08_haendler_kraeuter', 'location08', 3), ('Zwerg_Handwerker_loc09_zutatenhaendler', 'location09', 3)):
    m.place('Item', 'arm_tr_firefly_sac', 'npc', _npc, _lvl, stack=_n, tag='firefly')

# ======================= combat abilities (player, 2 Nov): the old class mod's attribute walls lowered =======================
# Lunge and Deadly Thrust are the light fighter's line, so they ask for little Courage. Power Throw is a thrower's skill: no
# Strength (the target still resists the knock-down with its own Strength). The parry line is cheaper, asks less and lasts.
ABILITIES = {
    'Klingensturm': dict(SkillRequirements='SF_Finte;MU/10;FF/12;IN/13;'),
    'GezielterStich': dict(SkillRequirements='SF_Finte;MU/9;IN/12;GE/13;'),
    'Todesstoss': dict(SkillRequirements='SF_GezielterStich;MU/10;IN/15;'),
    'Kraftwurf': dict(SkillRequirements='SF_GezielterWurf;FF/11;'),
    'MeisterParade': dict(SkillRequirements='PAbasis/8;', AU=8),
    'Klingenwand': dict(SkillRequirements='SF_Meisterparade;GE/12;', AU=15, XP=250, CombatBuffBonus=5),
    'Windmuehle': dict(SkillRequirements='SF_Klingenwand;GE/12;IN/12;', AU=20, CombatBuffBonus=3),
}
for _aid, _over in ABILITIES.items(): m.edit_vanilla('Attacks', _aid, **_over)
_EFFECT_TEXT = {'Klingenwand': [('4 extra parries', '5 extra parries'), ('additional 4 parries', 'additional 5 parries')],
                'Windmuehle': [('Two Parry and Dodge', 'Three Parry and Dodge')]}

# Tooltips: the "Requires:" line of every ability is rewritten from its real requirements (the old texts were hand-written and
# often wrong, e.g. Stormblade claimed ST 13). Attribute and ability names are the game's own English ones.
_ATTR = {'MU': 'CO', 'KL': 'CL', 'IN': 'IN', 'CH': 'CH', 'FF': 'DE', 'GE': 'AG', 'KO': 'CN', 'KK': 'ST',
         'ATbasis': 'Base AV', 'PAbasis': 'Base PA', 'FKbasis': 'Base RC'}
_loc = lambda k: (m.l.execute('select LocaText from _Locale where LocaId=?', (k,)).fetchone() or [None])[0]
_by_sf = {r['AtAttr']: r['Id'] for r in m.s.execute("select Id, AtAttr from _Template_Attacks where AtAttr like 'SF_%'")}
def _req_text(req):
    out = []
    for part in [p for p in (req or '').split(';') if p]:
        if part.startswith('SF_'):
            name = _loc(_by_sf[part]) if part in _by_sf else _loc(part)
            assert name, part
            out.append(name if 'Kampfstil' in part else f'SA {name}')
        else:
            a, v = part.split('/'); assert a in _ATTR, part
            out.append(f'{_ATTR[a]} {v}')
    return ', '.join(out)
for _r in m.s.execute("select Id, Description, SkillRequirements from _Template_Attacks where AtAttr like 'SF_%'").fetchall():   # enemy moves share texts
    _t = _loc(_r['Description'])
    if not _t or 'Requires:' not in _t: continue
    _req = ABILITIES.get(_r['Id'], {}).get('SkillRequirements', _r['SkillRequirements'])
    _new = re.sub(r'Requires:.*$', 'Requires: ' + (_req_text(_req) or 'nothing'), _t)
    for _a, _b in _EFFECT_TEXT.get(_r['Id'], []): _new = _new.replace(_a, _b)
    if _r['Id'] in ABILITIES and 'AU' in ABILITIES[_r['Id']]: _new = re.sub(r'ED Cost: \d+ EP', f"ED Cost: {ABILITIES[_r['Id']]['AU']} EP", _new)
    if _new != _t: m.vanilla_text(_r['Description'], _new)

# Sergeant Erland (Count's Town, both story versions) also teaches Lunge
for _nid in ('loc02_feldwebel_erland', 'loc02_feldwebel_erland_var_nach_loc05'):
    _ts = m.s.execute('select TeachableSkills from _Template_NPC where Id=?', (_nid,)).fetchone()['TeachableSkills']
    if 'SF_GezielterStich;' not in _ts: m.edit_vanilla('NPC', _nid, TeachableSkills=_ts.replace('SF_Finte;', 'SF_Finte;SF_GezielterStich;'))

# Gwendala knows Helpful Paw again: the old class mod set it to "not learned" on her (her template still says 3, vanilla 6)
for _g, _v in m.g.execute("select Guid, ZaTatzeSchwinge from _Instance_PC where Id='pc_gwendala'").fetchall():   # her world records only
    m.game.append(f"UPDATE _Instance_PC SET ZaTatzeSchwinge=3 WHERE Guid={lit(_g)};")
    m.undo_game.append(f"UPDATE _Instance_PC SET ZaTatzeSchwinge={lit(_v)} WHERE Guid={lit(_g)};")

# ======================= unique beasts and bosses: wound-immune, more willpower, life by story weight (tools/beasts_data.py) =======================
from beasts_data import TOUGH, toughened
for (_typ, _iid), _e in TOUGH.items():
    _r = m.s.execute(f'select * from _Template_{_typ} where Id=?', (_iid,)).fetchone()
    assert _r, _iid
    _new = toughened(dict(_r), _e)
    if _new: m.edit_vanilla(_typ, _iid, **_new)

m.check_collisions()
m.mirror_early()
m.write(out)
with open(os.path.join(out, 'icons', 'files.txt'), 'w', newline='\n') as f: f.write('\n'.join(icon_files) + '\n')
md = ['# Drakensang TDE Remastered: systems module', '', 'Install AFTER `mods/armory_v2` (uses its effects and items). New game required.', '',
      '| Kind | Item | Effect | How to get |', '|---|---|---|---|'] + [f'| {k} | **{n}** | {e} | {h} |' for k, n, e, h in catalogue]
md += ['', '## Skinning trophies (Animal Lore)', '', '| Loot table | Trophies | |', '|---|---|---|'] + [f'| `{t}` | {e} | {k} |' for t, e, k in skin_rows]
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('templates', len(m.templates), 'placed', len(m.instances), 'loot', len(m.loot_edits), 'status', len(m.se_names) - len(ARMORY_SE), 'icons', len(icon_files), 'catalogue', len(catalogue))
