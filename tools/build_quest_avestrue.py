"""Ulfried Pelzfeld, trophy collector (review 31 Oct, second pass).
- Ulfried travels like Gallo's package: Avestrue (Owlstone's spot), Ferdok (Praios Square), Tallon (next to the hunter) and Murolosh
  (next to the trader). All four share one quest line; hand trophies to whichever one you meet.
- Handed-in trophies are destroyed (DestroyEntity storageGroup PlayerParty), so they no longer show up in his shop for a copper.
- 1. Teeth for the Collector: 2 Wolf Fangs (White Fur always drops 2 + his own fang, see remastered_systems).
- 2. Beasts of Legend: five one-off elite beasts (placed monsters, no respawn), rewards scaled to their region.
- 3. The Grand Collection: trophies from the game's REAL unique monsters (Mother Ratzinsky, the oracle spider, the Gentle Sow's
  cockroach, the Marascan crab, the evil tree, the undead mule, the Grimmzahn vault spider, the Linnorm, the Ogre Chief, Japhgur,
  Aldessia's stone golem, the cyclops skeleton, the Grolm King's treasure). Their loot tables get a guaranteed unique trophy.
  Large monsters (Linnorm, Japhgur) cannot be skinned, so their trophies are corpse loot.
Usage: python -I tools/build_quest_avestrue.py "<game>/export/db/armory_backup" mods/quest_avestrue
Needs remastered_systems (Wolf Fang, Wolf-fang Necklace, trophies). New game required.
"""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, mods_text, make_icon, lit, insert
from quests import Story, ACTSEL as A

db, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(__file__)
m = Mod(db, 'questavestrue'); st = Story(m, 'questavestrue')
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
D = lambda d: int(d * 100)
icon_files = []
def icon(key, base_brush, tier):
    custom = os.path.join(HERE, '..', 'assets', 'remastered_icons', f'arm_{key}.dds')
    dst = os.path.join(out, 'icons', f'arm_{key}.dds')
    if os.path.isfile(custom): shutil.copy2(custom, dst)
    else: make_icon(os.path.join(HERE, 'research', 'out', 'icons_vanilla', base_brush.split('/')[-1] + '.dds'), dst, tier)
    icon_files.append(f'arm_{key}.dds'); return f'icons/arm_{key}'

TA = lambda did, take: f'TalkedAbout dialogId="{did}" takeId="{take}"; '
TDONE = lambda t, q: f'IsTaskClosed task="{t}" quest="{q}"; '
HAS = lambda iid, n: f'HasAmount category="Item" templateId="{iid}" operator="greaterOrEqual" count="{n}"; '
GIVE = lambda cat, iid, n=1: f'CreateEntity category="{cat}" templateId="{iid}" how="spawnInStorage" entity="Hero" number="{n}" executeAfter="true" {A}'
TAKE = lambda iid, n=1: (f'DestroyEntity category="Item" templateId="{iid}" count="{n}" storageGroup="PlayerParty" executeAfter="true" '
                         f'notInStorage="false" destroyDirectly="false" {A}')
GOLD = lambda d: f'GiveGold amount="{d * 100}" executeAfter="true" {A}'
XP = lambda n: f'GiveQuestXp questXp="{n}" {A}'
IMM = {'fire': 'Immune to burning', 'poison': 'Immune to poison', 'overthrown': 'Immune to knockdown', '': ''}

def trophy(tk, name, desc, quest):
    # quest item: cannot be sold, stolen or destroyed (a lost trophy would lock the quest for good; balance audit A6)
    m.template('Item', 'zutat_a_giftzahn', f'arm_{tk}', name, desc + '\\n\\nTrophy: Ulfried Pelzfeld, the trophy collector, will want it.',
               Value=0, Gew=10, QuestId=quest, CanDestroy=0, Robable=0, IconBrush=icon(tk, 'icons/alchimie_zutat_giftzahn', 'superrare'))
def reward(rk, base, name, desc, mods, imm, tier, typ='Jewelry', **stats):
    lines = '; '.join(x for x in (mods_text(mods), IMM[imm]) if x)
    pe = m.status('PeArm' + ''.join(w.capitalize() for w in rk.split('_')), name, lines, start=mods, immunity=imm)
    m.template(typ, base, f'arm_{rk}', name, desc + '\\n\\n' + lines.replace('; ', '\\n'), PermanentEffect=pe, Value=D(10),
               IconBrush=icon(rk, 'icons/magic_amulett_01', tier), **stats)

# ---------------- Beasts of Legend: one-off elite beasts, rewards scaled to the region (review: no early Constitution) ----------------
BEASTS = [  # key, display, base template, level, anchor, offset, stat changes, unique trophy (key, name, desc), extra drops, reward (key, base, name, desc, mods, imm, tier), hint, xp
    # moved out of Avestrue (the village closes after the prologue, so he could be missed for good; audit A7)
    ('grimtusk', 'Old Grimtusk', 'Wildschwein_loc01', 'location03',
     ('Monster', '|Level|Objects|Monster|unique|Josmene_Wildschwein_1', '_ID'), (5.0, 0, 4.0),
     dict(LE=100, LEmax=100, AT=15, PA=2, RSBr=4, MR=3, BasisXP=6, Stufe=4),
     ('tr_grimtusk', "Grimtusk's Tusk", 'A tusk as long as a forearm, scarred by a dozen hunters who did not come home.'),
     [('Item', 'arm_tr_boar_tusk', 100, 2, 1), ('Item', 'Wildschweinfell', 100, 1, 1)],
     ('tl_grimtusk', 'Silberkette', 'Grimtusk Charm', "Old Grimtusk's tusk bound in silver. You shrug off a little more.", 'LEmax +3 TaSelbstbeherrschung +2', '', 'amazing'),
     "Old Grimtusk, a boar the size of a cart, roams with the wild boars of the Blood Mountains, near Josmene's farm.", 20),
    ('ashpelt', 'Ashpelt the Elder', 'Baer_loc03', 'location03', ('MarkerPoint', 'loc03_marker_dunkelforst'), (6.0, 0, 0),
     dict(LE=170, LEmax=170, AT=18, PA=3, RSBr=5, MR=6, BasisXP=12, Stufe=10),
     ('tr_ashpelt', "Ashpelt's Claw", 'A grey-tipped claw from the oldest bear of the Dark Forest. It is warm, as if the bear still lived.'),
     [('Item', 'arm_tr_bear_claw', 100, 2, 1), ('Item', 'Baerenfell', 100, 1, 1)],
     ('tl_ashpelt', 'Goldkette', "Ashpelt's Talisman", 'The elder bear walks with you.', 'AUmax +8 LEmax +4', '', 'superrare'),
     'Ashpelt the Elder, a grey bear older than the witches, sleeps deep in the Dark Forest of the Blood Mountains.', 35),
    ('marshqueen', 'Queen of the Marsh', 'Loc03_DanosKroete', 'location04', ('MarkerPoint', 'loc04_marker_muehle'), (5.0, 0, 2.0),
     dict(LE=160, LEmax=160, AT=19, PA=2, RSBr=4, MR=10, BasisXP=12, Stufe=10, Faction='FaRaubtier'),
     ('tr_marsh_pearl', 'Marsh Pearl', 'A milky green pearl from the throat of the Queen of the Marsh. Spells seem to slide off it.'),
     [('Item', 'arm_tr_toad_wart', 100, 3, 1)],
     ('tl_marsh_pearl', 'Silberring', 'Marsh Pearl Ring', 'Bitter, cold and green. Magic and venom both struggle to reach you.', 'MR +2', 'poison', 'superrare'),
     'The Queen of the Marsh, a troll-toad as big as a hut, croaks near the old mill of Moorbridge.', 40),
    ('emberqueen', 'The Ember Queen', 'Feuerfliege_fett', 'location08', ('MarkerPoint', 'Mapmarker_loc08_Haendlerhoehle'), (5.0, 0, 0),
     dict(LE=260, LEmax=260, AT=19, PA=0, RSBr=3, MR=16, BasisXP=14, Stufe=12),   # audit B15: stronger than chapter 3's Ashpelt
     ('tr_ember_crown', 'Ember Crown', 'The glowing crest of the Ember Queen, mother of the Tallon fireflies. It never cools.'),
     [('Item', 'arm_tr_firefly_sac', 100, 3, 1)],
     ('tl_ember_crown', 'Goldkette', 'Ember Crown Pendant', 'A living ember in gold. Fire bows to you.', 'AEmax +8', 'fire', 'superrare'),
     'The Ember Queen, mother of all fireflies, nests by the traders\' cave near Tallon.', 45),
    ('broodmother', 'The Broodmother', 'Smaragdspinne_loc11', 'location11', ('MarkerPoint', 'marker_kristall_3'), (6.0, 0, 0),
     dict(LE=520, LEmax=520, AT=23, PA=2, RSBr=6, MR=15, BasisXP=20, Stufe=17),
     ('tr_brood_heart', "Broodmother's Heart", 'An emerald heart the size of a fist. It still beats, slowly.'),
     [('Item', 'arm_tr_spider_eye', 100, 3, 1)],
     ('tl_brood_heart', 'Goldkette', "Broodmother's Heart", 'Eight-eyed patience, quick as a strike. Venom is your friend now.', 'GE +2 FF +1 AW +1', 'poison', 'legendary'),
     'The Broodmother, the great emerald spider, guards the crystal caves behind the Fire Falls.', 60),
]
for key, disp, base, lvl, anchor, off, over, (tk, tname, tdesc), drops, (rk, rbase, rname, rdesc, rmods, rimm, tier), hint, xp in BEASTS:
    trophy(tk, tname, tdesc, 'arm_q_ulfried_legends')
    lt = st.loot_table(f'arm_lt_{key}', [('Item', f'arm_{tk}', 100, 1, 1)] + drops)
    # unique beasts resist wounds and carry a third more life (review 1 Nov, tools/beasts_data.py)
    _imm = (m.s.execute('select Immunity from _Template_Monster where Id=?', (base,)).fetchone()[0] or '').split(';')
    over = dict(over, LE=int(over['LE'] * 1.3), LEmax=int(over['LEmax'] * 1.3),
                Immunity=';'.join(dict.fromkeys(x for x in _imm + (over.get('Immunity') or '').split(';') + ['wound'] if x)))
    st.monster(f'arm_mo_{key}', disp, base, lvl, anchor, off, info=hint, LootTable=lt, **over)
    reward(rk, rbase, rname, rdesc, rmods, rimm, tier)
HEART = 'LEmax +10 AUmax +10 MU +1 TaTierkunde +3 TaPflanzenkunde +3 TaWildnisleben +3'
reward('tl_heart_wild', 'Goldkette', 'Heart of the Wild', "Ulfried's masterpiece: a fang, a tusk, a claw, a pearl, an ember and an emerald heart, "
       "bound into one. The wild knows you now.", HEART, '', 'legendary')

# ---------------- The Grand Collection: the real unique monsters of the game ----------------
def override_loot(typ, iid, key, ours, lootable=False):
    """Give one monster/NPC its own loot table = its old table + our entries, every entry dropping (pick count = all entries)."""
    cur = m.s.execute(f'select LootTable from _Template_{typ} where Id=?', (iid,)).fetchone()
    assert cur is not None, (typ, iid)
    old = m.loot_tables().get(cur[0], ('0', ''))[1] if cur[0] else ''
    olde = [e for e in old.split(';') if e]
    content = ''.join(e + ';' for e in olde) + ''.join(f'{t}/{i}/{c}/{n}/{v}/;' for t, i, c, n, v in ours)
    name = f'arm_lt_{key}'
    m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(name)};",
                 f"INSERT INTO _DSA_LootTables (LootTableName, LootTableValue, LootTableContent) VALUES ({lit(name)}, {lit(str(len(olde) + len(ours)))}, {lit(content)});"]
    m.undo_static.append(f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(name)};")
    m.edit_vanilla(typ, iid, LootTable=name, **({'IsLootable': 1} if lootable else {}))
COLLECTION = [  # key, trophy (key, name, desc), source, reward (key, base, name, desc, mods, imm, tier[, type, stats]), hint, xp
    ('ratzinsky', ('tr_ratzinsky', "Mother Ratzinsky's Iron Tooth", 'An iron-hard incisor from the rat-mother of Ferdok. It still smells of the sewers.'),
     ('Monster', 'Wolfsratte_loc02_mutter_ratzinski', [('Jewelry', 'arm_j_rat_crown', 100, 1, 1)]),
     ('c_ratzinsky', 'Silberkette', "Rat-Queen's Cameo", 'A cameo carved from her tooth. Sewers, cellars and pockets hold no secrets from you.', 'TaSchleichen +2 TaTaschendiebstahl +2 AUmax +5', '', 'amazing'),
     'Mother Ratzinsky, the monstrous rat-mother, rules the cellars of the Ferdok rat plague.', 25),
    ('cockroach', ('tr_cockroach', 'Carapace of the Gentle Sow', 'A shard of the giant cockroach that terrorised the Gentle Sow. The innkeeper wants it framed.'),
     ('Monster', 'Gruftassel_gross_loc02_sanfte_sau_schabe', []),
     ('c_cockroach', 'Silberring', "Tavern-Brawler's Ring", 'A ring of cockroach shell. Nothing in a tavern can hurt you any more, not even the stew.', 'AUmax +5 TaSelbstbeherrschung +3', 'poison', 'amazing'),
     'The giant cockroach in the cellar of the Gentle Sow tavern in Ferdok.', 20),
    ('oracle', ('tr_oracle_eye', "Oracle Spider's Eye", 'A faceted green eye from the emerald spider that lairs beneath the oracle of Ferdok.'),
     ('Monster', 'Smaragdspinne_loc02', []),
     ('c_oracle', 'Silberkette', "Seer's Eye Pendant", 'The oracle spider\'s eye in silver. You notice things a moment before they happen.', 'IN +1 TaSinnenschaerfe +3', '', 'superrare'),
     'The emerald spider in the caves beneath the oracle of Ferdok.', 30),
    ('marascan', ('tr_marascan_claw', 'Marascan Crab Claw', 'A claw of the Marascan giant crab of Ferdok harbour, big enough to cut an oar in half.'),
     ('Monster', 'Riesenkrabbe_loc02', []),
     ('c_marascan', 'Silberring', 'Harbour-Claw Ring', 'A ring cut from the claw. Blows glance off you like waves off the pier.', 'PA +1 AUmax +3', '', 'amazing'),
     'The Marascan giant crab that lurks in Ferdok harbour.', 25),
    ('evil_tree', ('tr_evil_heartwood', 'Heartwood of the Evil Tree', 'Black, oily heartwood from the evil tree of Moorbridge. It is still whispering.'),
     ('Monster', 'boeser_baum', []),
     ('c_evil_tree', 'Silberkette', 'Witchwood Charm', 'A sliver of the whispering wood. It listens to spells, and argues with them.', 'MR +2 AEmax +5', '', 'superrare'),
     'The evil tree that grips the marshes of Moorbridge.', 30),
    ('mule', ('tr_mule_bell', 'Bell of the Undead Mule', 'The cracked bell of the undead mule of Moorbridge. It rings on its own at midnight.'),
     ('Monster', 'Untotes_Maultier', []),
     ('c_mule', 'Silberkette', 'Mule-Bell of Stubbornness', 'The mule refused to stay dead. Now you refuse things too. Mostly reasonable advice.', 'KO +1 TaSelbstbeherrschung +3 CH -1', '', 'superrare'),
     'The undead mule that still walks the roads of Moorbridge.', 25),
    ('vault_spider', ('tr_vault_mandible', "Vault Spider's Mandible", 'A mandible of the emerald spider in the vaults of Castle Grimmzahn.'),
     ('Monster', 'Smaragdspinne_loc05', []),
     ('c_vault_spider', 'Goldring', 'Mandible Ring', 'Two mandibles closing on a gem. Your blows land where you mean them to.', 'AT +1 FF +1', '', 'superrare'),
     'The emerald spider in the vaults of Castle Grimmzahn.', 35),
    ('linnorm', ('tr_linnorm_heart', "Linnorm's Heart", 'The heart of the Linnorm of the Stinking Caves near Tallon, dried hard as wood. It still feels warm.'),
     ('MonsterLarge', 'Tatzelwurm_v2', [('Item', 'arm_tr_tatzel_fang', 100, 2, 1)]),
     ('c_linnorm', 'Goldkette', 'Linnorm-Heart Amulet', 'You carry the courage of a creature that fought you to the last.', 'MU +2 LEmax +10', '', 'legendary'),
     'The Linnorm in the Stinking Caves near Tallon.', 50),
    ('ogre', ('tr_ogre_tusk', "Ogre Chief's Tusk", 'A yellow tusk of the Ogre Chief of Tallon, as thick as a wrist.'),
     ('NPC', 'Oger_04_kraeftig_loc08_boss', []),
     ('c_ogre', 'Goldkette', 'Ogre-Tusk Torc', 'Heavy, crude and immensely strong, like its first owner. Swing hard; aim later.', 'KK +1 LEmax +10 AT -1', '', 'superrare'),   # audit A4: Forgrimm Strength budget
     'The Ogre Chief in the ogre camp near Tallon.', 45),
    ('japhgur', ('tr_dragon_eye', 'Eye of Japhgur', 'The eye of the Purplewyrm Japhgur, the size of a shield boss. It never closes.'),
     ('MonsterLarge', 'Japhgur', [('Item', 'arm_tr_wyrm_horn', 100, 1, 1)]),
     ('c_japhgur', 'Goldkette', 'Wyrmeye Amulet', 'The dragon\'s eye in gold. Fire, magic and blades all seem slower now.', 'IN +2 MR +3 AW +1', 'fire', 'legendary'),
     'Japhgur, the Purplewyrm, in his lair near Tallon.', 80),
    ('golem', ('tr_golem_heart', 'Golem Heartstone', 'The rune-stone heart of a stone golem from Aldessia\'s chambers in Murolosh.'),
     ('NPC', 'Steingolem_loc09_aldessia', []),
     ('c_golem', 'Goldring', 'Heartstone Ring', 'A ring of golem stone. You are a little more stone yourself.', 'KO +2 MR +1', '', 'superrare'),
     'The stone golems in Aldessia\'s chambers in Murolosh.', 45),
    ('cyclops', ('tr_cyclops_gem', 'Cyclops Eye-Gem', 'The gem that sat in the single eye socket of the cyclops skeleton in the Deeps of Gruldur.'),
     ('loot', 'loot_unique_Zyklopenskelett_loc10', []),
     ('c_cyclops', 'Goldring', "Cyclops'-Eye Ring", 'One eye sees further than two. Your shots fly true.', 'FF +2 IN +1 TaBogen +2', '', 'legendary'),
     'The cyclops skeleton in the Deeps of Gruldur.', 60),
    ('grolm', ('tr_grolm_shard', "Grolm King's Crown-Shard", 'A shard of the Grolm King\'s crown, hidden in his treasure chests behind the Fire Falls.'),
     ('loot', 'loot_loc11_truhe_4', []),
     ('c_grolm', 'Goldring', "Grolm King's Signet", 'Grolms bargain for a living. This ring has never lost a bargain.', 'CH +2 TaFeilschen +5 TaUeberreden +3', '', 'legendary'),
     'The Grolm King\'s treasure chests behind the Fire Falls.', 60),
]
# Mother Ratzinsky's own amulet (review: her long quest only gave a ring of life)
reward('j_rat_crown', 'Silberkette', 'Crown of the Rat Mother', "Mother Ratzinsky's iron crown, shrunk to an amulet by the rust of the sewers. Disease and poison bow to it.",
       'LEmax +5 TaSelbstbeherrschung +2', 'poison', 'superrare')
for key, (tk, tname, tdesc), (styp, sid, extra), (rk, rbase, rname, rdesc, rmods, rimm, tier), hint, xp in COLLECTION:
    trophy(tk, tname, tdesc, 'arm_q_ulfried_collection')
    ours = [('Item', f'arm_{tk}', 100, 1, 1)] + extra
    if styp == 'loot':
        for t, i, c, n, v in ours: m.loot(sid, t, i, mode='all', chance=c, amount=n)
    else:
        override_loot(styp, sid, key, ours, lootable=(styp == 'MonsterLarge'))
    reward(rk, rbase, rname, rdesc, rmods, rimm, tier)
MANTLE = 'LEmax +10 AUmax +10 MU +1 TaTierkunde +3'
# audit N8: the end of the collection gives a book of lore, one entry per legend (the player reads lore; gold was dead weight)
LORE = {'ratzinsky': "Mother Ratzinsky ruled the cellars of Ferdok for nine winters. Her iron tooth hangs over my door; no rat has come near since.",
        'cockroach': "The cockroach of the Gentle Sow ate three hams, a barrel of pickles and a tax collector's ledger. Only the ledger was missed.",
        'oracle': "The spider below the oracle wove its webs in the shape of prophecies. None of them came true. Spiders are poor seers.",
        'marascan': "The Marascan crab cut a fishing boat in two in the year of the long winter. The fishermen still owe it a boat.",
        'evil_tree': "The evil tree of Moorbridge whispered every night. I wrote down what it said. I burned what I wrote.",
        'mule': "The undead mule refused to die, to move, or to carry anything. In this it was no different from a living mule.",
        'vault_spider': "The spider of Grimmzahn's vaults grew fat on orcs. The orcs, to be fair, grew fat on everything else.",
        'linnorm': "The Linnorm of the Stinking Caves was old when Tallon was a village. It is the only beast in this book I am sorry we killed.",
        'ogre': "The Ogre Chief of Tallon wore his tusks as a crown and his enemies as a cloak. You have neither now. Good.",
        'japhgur': "Japhgur the Purplewyrm. Its eye watched Tallon burn twice. It will not watch again. I have it, in a jar, and it still watches me.",
        'golem': "Aldessia's golems were built to guard and nothing else. The heartstone is warm, as if it still remembers its orders.",
        'cyclops': "The cyclops of Gruldur fell before the dwarves had a name. Its eye-gem shows a forge that no longer exists.",
        'grolm': "The Grolm King hoarded crowns he never wore. This shard is from the only one he loved. I will not tell you how I know."}
# books have their own columns (BookText, Name = display key, no InfoIdentified): insert the row directly
_bk = dict(m.s.execute("select * from _Template_Book where Id='loc01_brief_ardo'").fetchone())
_bk.update(Id='arm_q_beast_ledger', Name='name_arm_q_beast_ledger', LookAtText='lookat_arm_q_beast_ledger', BookText='text_arm_q_beast_ledger',
           QuestId='NONE', Sound='', Value=0, IconBrush=icon('q_beast_ledger', 'icons/questitem_briefumschlag', 'legendary'))
m.static += ["DELETE FROM _Template_Book WHERE Id='arm_q_beast_ledger';", insert('_Template_Book', _bk)]
m.undo_static.append("DELETE FROM _Template_Book WHERE Id='arm_q_beast_ledger';")
m.text('name_arm_q_beast_ledger', "Ulfried's Ledger of Beasts"); m.text('lookat_arm_q_beast_ledger', "Ulfried's Ledger of Beasts")
m.text('text_arm_q_beast_ledger', "THE GRAND COLLECTION OF ULFRIED PELZFELD\\n\\n" + '\\n\\n'.join(LORE[c[0]] for c in COLLECTION)
       + "\\n\\nAll of it brought by one hunter. I have stopped telling people who. They would not believe me anyway.")
reward('c_mantle', 'schultern_nasreddin', 'Mantle of a Thousand Trophies', "Ulfried's life's work: a mantle stitched with a scrap of every legend you brought him. "
       "Hunters bow when you pass.", MANTLE, '', 'legendary', typ='Armor')

# No spoilers (review 1 Nov): what Ulfried says and what the journal shows are vague riddles, never a name or an exact place.
# The explicit hints above stay only on the beast itself (its look-at text), where the player has already found it.
VAGUE = {  # key -> (journal title, riddle)
    'grimtusk': ('The Great Boar', 'A boar the size of a cart, scarred by a dozen hunters who did not come home, roams the hills where farmers fence their fields twice.'),
    'ashpelt': ('The Grey Bear', 'The oldest bear alive sleeps somewhere dark and green, where even hunters walk quietly.'),
    'marshqueen': ('The Croaking Queen', 'Somewhere wet and grey, a queen croaks louder than the bells, close to an old building nobody uses.'),
    'emberqueen': ('The Glowing Mother', 'Where the small lights dance thickest at night, far from here, their mother nests in the warm dark.'),
    'broodmother': ('The Patient Mother', 'Far beyond anywhere you have been, a mother guards her treasures in the dark. Only if you are mad.'),
    'ratzinsky': ('The Mother Below', 'Something under the city breeds faster than the city can count. Find the one that started it.'),
    'cockroach': ('The Tavern Pest', 'A tavern in the city has a cellar problem the innkeeper would rather not talk about.'),
    'oracle': ('The Watcher Below', 'Something lives beneath the place where people go to ask about the future.'),
    'marascan': ('The Harbour Terror', 'Fishermen whisper about something in the harbour water.'),
    'evil_tree': ('The Whispering Wood', 'Somewhere the ground is never dry, a tree whispers at night. Trees should not whisper.'),
    'mule': ('The Stubborn Dead', 'A beast of burden that refused to stay dead still walks somewhere it should not.'),
    'vault_spider': ('Something in the Vaults', 'An old castle keeps something in its vaults, grown fat on whoever lives there now.'),
    'linnorm': ('The Old One', 'In caves you smell long before you see them, something very old is waiting.'),
    'ogre': ('The Tusked Chief', 'Big, hungry folk have a chief who wears his tusks like a crown. Find their camp.'),
    'japhgur': ('The Eye That Watches', 'Every land has one creature nobody dares to name. If you ever meet it, bring me its eye.'),
    'golem': ('The Heart of Stone', 'Somewhere under the mountains, guardians still follow orders nobody gives any more. Bring me a heart of stone.'),
    'cyclops': ('The Old Bones', 'In the oldest halls under the mountains lie bones nobody can name. Something precious was left among them.'),
    'grolm': ('The Hoarder\'s Crown', 'Small, greedy folk who haggle over everything have a king, and his chests hold a broken crown.'),
}

# ---------------- the travelling Ulfried ----------------
Q1, T1 = 'arm_q_ulfried', 'arm_q_ulfried_fangs'
Q2, Q3 = 'arm_q_ulfried_legends', 'arm_q_ulfried_collection'
SPOTS = {  # dialog id -> npc id, level, anchor, offset, greeting
    'arm_dlg_ulfried': ('arm_npc_ulfried', 'location01', ('MarkerPoint', 'loc01_marker_kautzenstein_2'), (2.5, 0, 1.5),
                        "Ah, a traveller with sharp eyes and, I hope, a sharp knife! Ulfried Pelzfeld, collector of trophies, curiosities and anything with teeth. "
                        "Avestrue's woods are full of wolves, and wolves are full of fangs."),
    'arm_dlg_ulfried_f': ('arm_npc_ulfried_f', 'location02_praios', ('NPC', 'loc02_trainer_praios_bogen'), (2.5, 0, 1.0),
                          "Ulfried Pelzfeld, collector of trophies! I follow the hunters, and the hunters follow the money, so here I am in Ferdok. "
                          "Bring me anything with teeth, wherever you found it."),
    'arm_dlg_ulfried_t': ('arm_npc_ulfried_t', 'location08', ('NPC', 'loc08_jaeger'), (2.5, 0, 1.0),
                          "What a place! Everything within a day's walk has bigger teeth than the last. I have not been this happy since my first wolf. What did you bring me?"),
    'arm_dlg_ulfried_m': ('arm_npc_ulfried_m', 'location09', ('NPC', 'Loc09_Zwergenhaendler'), (2.5, 0, 1.0),
                          "The dwarves keep asking what I collect. 'Everything,' I say, and they nod as if that were sensible. Show me your trophies, friend."),
}
DIALOGS = list(SPOTS)
ANY = lambda take: [TA(d, take) for d in DIALOGS]             # Or-group: said in any Ulfried's dialog
NONE = lambda take: ['!' + TA(d, take) for d in DIALOGS]      # said in none of them
for did, (nid, lvl, anchor, off, hello) in SPOTS.items():
    st.npc(nid, 'Ulfried Pelzfeld, Trophy Collector', 'Jaeger_Kauzenstein_loc08_jaeger', lvl, anchor, off, merchant=True, ScriptPreset='')
    for typ, iid, n in (('Item', 'special_kuerschnermesser', 1), ('Item', 'Wolfsfell', 3), ('Item', 'zutat_b_sehnen', 10), ('Item', 'zutat_s_lederbaender', 10)):
        st.stock(nid, typ, iid, n)
    HUB = (['r_job', 'r_turnin', 'r_legend', 'r_coll'] + [f'r_{b[0]}' for b in BEASTS] + [f'r_c_{c[0]}' for c in COLLECTION]
           + ['r_heart', 'r_mantle', 'r_where', 'r_trade', 'r_bye'])
    takes = [
        dict(id='StartState', type='StartState', kids=['t_return', 't_first']),
        dict(id='t_first', type='Take', kids=HUB, text=hello),
        dict(id='t_return', type='Take', kids=HUB, cond=[TA(did, 't_first')], text="Back again, <FirstName>! Did you bring me something with teeth?"),
        dict(id='r_job', type='Response', kids=['t_offer'], cond=NONE('r_accept'), text='Do you have work for me?'),
        dict(id='t_offer', type='Take', kids=['r_accept', 'r_bye'],
             text="Bring me two wolf fangs. Skin the wolves around Avestrue; a furrier's knife helps, and Owlstone sells one, as do I. "
                  "White Fur herself has a fine pair, and more besides. I pay in silver, and in something better."),
        dict(id='r_accept', type='Response', kids=['t_accepted'], text='Two wolf fangs. Consider it done.'),
        dict(id='t_accepted', type='Take', kids=['r_trade', 'r_bye'], text="Splendid! Mind the white one. She is bigger than the stories."),
        dict(id='r_turnin', type='Response', kids=['t_thanks'], cond=[ANY('r_accept'), HAS('arm_tr_wolf_fang', 2)] + NONE('t_thanks'),
             text='I have your wolf fangs.'),
        dict(id='t_thanks', type='Take', kids=['r_legend', 'r_coll', 'r_trade', 'r_bye'], act=TAKE('arm_tr_wolf_fang', 2) + GIVE('Jewelry', 'arm_tl_wolf') + GOLD(10),
             text="Beautiful fangs! Here: a necklace I made from the last pair, and some silver. And now that I know you can hunt, I have bigger plans for us. "
                  "Oh, and between us: the chickens of Avestrue are not what they seem."),
        dict(id='r_legend', type='Response', kids=['t_legend'], cond=[ANY('t_thanks')] + NONE('r_legend_ok'), text='Bigger plans?'),
        dict(id='t_legend', type='Take', kids=['r_legend_ok', 'r_bye'],
             text="Five beasts, friend. Five legends every hunter tells at the fire, and nobody has a trophy of. A great boar, an old bear, "
                  "a queen who croaks, a mother who glows, and one more I will not name until you are ready for her. Where exactly? If I knew, "
                  "I would be rich. Bring me their trophies and I will make you talismans no king owns."),
        dict(id='r_legend_ok', type='Response', kids=['t_legend_ok'], text='I will hunt your legends.'),
        dict(id='t_legend_ok', type='Take', kids=['r_coll', 'r_trade', 'r_bye'], text="Ha! Then I had better start sharpening my tools. Bring them one at a time; each is a masterpiece."),
        dict(id='r_coll', type='Response', kids=['t_coll'], cond=[ANY('t_thanks')] + NONE('r_coll_ok'), text='What else does a collector collect?'),
        dict(id='t_coll', type='Take', kids=['r_coll_ok', 'r_bye'],
             text="Everything that has ever made a town lock its doors! Thirteen of them. Some are closer than you think: in the city, under it, "
                  "and in its water. Others you will meet only if your road goes far, and I think it will. I follow the hunters, so look for me "
                  "wherever the game gets bigger. Bring me one trophy of each. Your journal will keep my riddles."),
        dict(id='r_coll_ok', type='Response', kids=['t_coll_ok'], text='Your Grand Collection. I will fill it.'),
        dict(id='t_coll_ok', type='Take', kids=['r_where', 'r_trade', 'r_bye'], text="Then we shall be famous! Or eaten. Probably famous."),
        dict(id='r_where', type='Response', kids=['t_where'], cond=[ANY('r_coll_ok')], text='Any advice on finding your monsters?'),
        dict(id='t_where', type='Take', kids=HUB,
             text="Advice? Listen to frightened people. Wherever doors are locked at night and children are told not to go somewhere, one of my beasts is close. "
                  "Start with the city, and keep your eyes open on the road. My riddles are in your journal."),
    ]
    for key, disp, base, lvl2, anchor2, off2, over, (tk, tname, _), drops, (rk, _, rname, _, _, _, _), hint, xp in BEASTS:
        takes += [dict(id=f'r_{key}', type='Response', kids=[f't_{key}'], cond=[ANY('r_legend_ok'), HAS(f'arm_{tk}', 1)] + NONE(f't_{key}'),
                       text=f"{disp} is dead. I brought you this: {tname}."),
                  dict(id=f't_{key}', type='Take', kids=HUB[2:], act=TAKE(f'arm_{tk}') + GIVE('Jewelry', f'arm_{rk}'),
                       text=f"{disp}! By Firun's beard, you really did it. Give me a moment... there. The {rname}. Wear it with pride.")]
    for key, (tk, tname, _), _src, (rk, *_r), hint, xp in COLLECTION:
        rname = _r[1]
        takes += [dict(id=f'r_c_{key}', type='Response', kids=[f't_c_{key}'], cond=[ANY('r_coll_ok'), HAS(f'arm_{tk}', 1)] + NONE(f't_c_{key}'),
                       text=f"For your Grand Collection: {tname}."),
                  dict(id=f't_c_{key}', type='Take', kids=HUB[2:], act=TAKE(f'arm_{tk}') + GIVE('Jewelry', f'arm_{rk}') + GOLD(xp // 2),
                       text=f"Oh! Oh, look at it. Into the collection it goes, with a label in my best hand. For you: the {rname}, and a purse for the road.")]
    takes += [
        dict(id='r_heart', type='Response', kids=['t_heart'], cond=[TDONE(f'{Q2}_{b[0]}', Q2) for b in BEASTS] + NONE('t_heart'),
             text='That was the last of your five legends.'),
        dict(id='t_heart', type='Take', kids=HUB[2:], act=GIVE('Jewelry', 'arm_tl_heart_wild') + GOLD(50),
             text="All five. Nobody will believe me, and I do not care. I kept a piece of each; this is the best thing I have ever made. Take it. "
                  "The Heart of the Wild. And some gold, because legends still have to eat."),
        dict(id='r_mantle', type='Response', kids=['t_mantle'], cond=[TDONE(f'{Q3}_{c[0]}', Q3) for c in COLLECTION] + NONE('t_mantle'),
             text='That completes your Grand Collection.'),
        dict(id='t_mantle', type='Take', kids=['r_trade', 'r_bye'], act=GIVE('Armor', 'arm_c_mantle') + GIVE('Book', 'arm_q_beast_ledger') + GOLD(100),
             text="Complete. The Grand Collection of Ulfried Pelzfeld, and every piece in it brought by one hunter. I sewed a scrap of each into this mantle. "
                  "Wear it, and every hunter from here to the deepest dwarf hall will know who you are."),
        dict(id='r_trade', type='Response', act=f'ShowTradeUI trader="{nid}" executeAfter="true" {A}', text='Show me your wares.'),
        dict(id='r_bye', type='Response', text='Farewell, Ulfried.'),
    ]
    st.dialog(did, nid, takes)

st.task(Q1, 'Teeth for the Collector', 'Ulfried Pelzfeld, a travelling trophy collector who follows the hunters, wants trophies from the local wolves.',
        'Ulfried paid me well for the wolf fangs and hinted at bigger game.', open_cond=[ANY('r_accept')], close_cond=[TDONE(T1, Q1)])
st.task(T1, 'Two Wolf Fangs', 'Bring Ulfried two Wolf Fangs. Skinning wolves (Animal Lore) yields fangs; the white wolf White Fur always carries a pair. '
        'Ulfried waits next to Owlstone in Avestrue, and later on Praios Square in Ferdok.',
        'I gave Ulfried two Wolf Fangs.', parent=Q1, state='unlocked', close_cond=[ANY('t_thanks')], close_act=XP(15), target='arm_npc_ulfried')
st.task(Q2, 'Beasts of Legend', 'Ulfried wants trophies from five legendary beasts.', 'All five legends are hunted. Ulfried made me the Heart of the Wild.',
        open_cond=[ANY('r_legend_ok')], close_cond=[ANY('t_heart')])
for key, disp, *_rest in BEASTS:
    xp = _rest[-1]; title, riddle = VAGUE[key]
    st.task(f'{Q2}_{key}', title, riddle + ' Bring its trophy to Ulfried.', f'Ulfried has the trophy of {disp}.', parent=Q2, state='unlocked',
            close_cond=[ANY(f't_{key}')], close_act=XP(xp))
st.task(Q3, 'The Grand Collection', 'Ulfried wants one trophy from every monster that ever made a town lock its doors. He follows the hunters, '
        'so look for him wherever the game gets bigger.', 'The Grand Collection is complete. Ulfried gave me the Mantle of a Thousand Trophies.',
        open_cond=[ANY('r_coll_ok')], close_cond=[ANY('t_mantle')])
for key, (tk, tname, _), _src, _rw, hint, xp in COLLECTION:
    title, riddle = VAGUE[key]
    st.task(f'{Q3}_{key}', title, riddle + ' Bring the trophy to Ulfried.', f'{tname} is in the Grand Collection.', parent=Q3, state='unlocked',
            close_cond=[ANY(f't_c_{key}')], close_act=XP(xp))

m.write(out)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('\n'.join(icon_files) + '\n')
rw = lambda r: f'{r[2]}: ' + '; '.join(x for x in (mods_text(r[4]), IMM[r[5]]) if x)
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write(
    '# Ulfried Pelzfeld, trophy collector\n\nUlfried travels with the hunters: Avestrue (by Owlstone), Ferdok (Praios Square, by the bowyer), Tallon (by the hunter) '
    'and Murolosh (by the trader). All four share one quest line. Handed-in trophies are kept by him (they do not reappear in his shop).\n\n'
    '## Teeth for the Collector\nBring 2 Wolf Fangs (skinning, or White Fur, who always drops 2 plus his own great fang). Reward: Wolf-fang Necklace, 10 ducats, 15 XP.\n\n'
    '## Beasts of Legend\nFive one-off elite beasts with unique trophies:\n\n| Beast | Where | Talisman |\n|---|---|---|\n'
    + ''.join(f'| {b[1]} | {b[11]} | {rw(b[9])} |\n' for b in BEASTS) + f'\nAll five: **Heart of the Wild** ({mods_text(HEART)}) and 50 ducats.\n\n'
    '## The Grand Collection\nThe real unique monsters of the game now drop a trophy (Linnorm and Japhgur on their corpse, they cannot be skinned):\n\n'
    '| Monster | Where | Reward |\n|---|---|---|\n' + ''.join(f'| {c[1][1]} | {c[4]} | {rw(c[3])} |\n' for c in COLLECTION)
    + f'\nMother Ratzinsky also drops the **Crown of the Rat Mother** (LE +5, Self-control +2, immune to poison).\n'
    f'All thirteen: **Mantle of a Thousand Trophies** ({mods_text(MANTLE)}) and 100 ducats.\n')
print('ok static', len(m.static), 'game', len(m.game), 'texts', len(m.locale), 'icons', len(icon_files))
