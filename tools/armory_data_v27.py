# v2.7 rebalance (1-2 Nov, docs/REBALANCE_PLAN.md batches 1-3, answered by the player). Exec'd last by armory_data.py.
# Rules: one improvement per stage step; big leather plans found in Grimmzahn's armoury or sold in Tallon; no Survival anywhere and
# no gathering bonus on looted gear; boss relics with their plans on the boss; every craftable gets an in-world story.
_K = {it['key']: it for it in ITEMS}
def _set(key, **kw):
    it = _K[key]
    st = kw.pop('stats', None)
    if st is not None:
        for k, v in st.items():
            if v is None: it['stats'].pop(k, None)
            else: it['stats'][k] = v
    rec = kw.pop('recipe', None)
    if rec is not None: it['recipe'].update(rec)
    it.update(kw)
GRIMMZAHN_RACK = 'loot_loc05_waffenkammer_ammo'      # the ammunition rack in Grimmzahn's armoury (war and incendiary arrows)
LOOT_EXTRA = []        # (loot table, type, id): added with mode 'all' by build_armory
LOOT_OWN = {}          # (template type, id) -> [(type, id, chance, amount)]: the boss gets its own table = old loot + these
def _found_at(table, key):   # a plan that is found, not sold
    _K[key]['recipe']['sellers'] = []; LOOT_EXTRA.append((table, 'Recipe', f'arm_rezept_{key}'))

# ---------------- B1.1 the big-leather gate ----------------
for _k in ('a_iryan_greaves', 'a_ranger_breeches', 'a_duelist_grips', 'ts_bracers', 'wp_jerkin', 'wp_breeches', 'wp_grips'):
    _found_at(GRIMMZAHN_RACK, _k)
for _k in ('ts_cuirass', 'ts_helm'): _K[_k]['recipe']['sellers'] = [TALLON_CRAFT]
for _k in ('mh_jerkin', 'mh_breeches', 'mh_grips'): _K[_k]['recipe']['sellers'] = [TALLON_HUNTER]   # Moonhowl body pieces build on Darkwolf
for _k in ('tw_bracers', 'tw_helm'): _K[_k]['recipe']['sellers'] = [MUROLOSH_SMITH]
for _k in ('a_iryan_greaves', 'a_ranger_breeches', 'a_duelist_grips', 'ts_bracers', 'wp_jerkin', 'wp_breeches', 'wp_grips'): _K[_k]['stage'] = 1   # armour-rule stages: 0 early, 1 mid, 2 late, 3 endgame

# ---------------- B1.2 - B1.3 leather pieces ----------------
_set('a_ranger_breeches', tier='superrare', mods='AW +1', recipe=dict(mats=[(DARKPELT, 2), (ISINEW, 1)], diff=10))
_set('a_duelist_grips', tier='superrare', mods='PA +1', stats=dict(RSLA=3, RSRA=3), recipe=dict(mats=[(STRIPS, 2), (TUSK, 2)], diff=10))
_set('a_iryan_greaves', tier='superrare', mods='', stats=dict(RSLB=3, RSRB=3), recipe=dict(mats=[(STRIPS, 3), (STEEL, 1)], diff=10))
_set('wp_breeches', mods='TaSinnenschaerfe +2', stats=dict(RSBa=1, RSLB=2, RSRB=2))      # Grimmzahn: 5, the vanilla mark there
_set('wp_grips', mods='TaBogen +1', stats=dict(RSLA=2, RSRA=2))
_set('wp_jerkin', mods='TaSchleichen +2 AUmax +5')

# ---------------- B1.4 White Fur Mantle: two paths from tier I ----------------
_set('wp_mantle', mods='MR +1', stats=dict(RSBr=None, RSRu=None, RSLA=1, RSRA=1, ArBE=0.1))
RATTEL, TINCTURE, SUNSEAL, CINDER, OGREHIDE, GOLEMHEART = ('arm_rl_rattel_pelt', 'arm_rl_silver_tincture', 'arm_rl_sunseal',
                                                         'arm_rl_cult_cinder', 'arm_rl_ogre_hide', 'arm_rl_golem_heart')
MATERIALS += [
    ('rl_rattel_pelt', 'Wolfsfell', "Pelt of Duskmane", "The pelt of Duskmane, the old pack-lord of the Rattelshof hills, grey at the muzzle and black down the spine. "
     "Hunters say he was never caught because he was never once in a hurry.", 2000, []),
    ('rl_silver_tincture', 'zutat_a_alkohol', "Aldessia's Silver Tincture", "A stoppered flask of quicksilver-white fluid, labelled in a careful hand: "
     "'Fixes hide, fur and hair against any rot. Do NOT drink.' Someone drank. The label was revised.", 3000, []),
    ('rl_sunseal', 'zutat_s_blattgold', "Inquisitor's Sun-Seal", "A heavy gold seal of the Praios church, blessed so often that magic slides off it. "
     "The Grand Inquisitor pressed it into the wax of every warrant he signed.", 2500, []),
    ('rl_cult_cinder', 'zutat_b_zunderschwamm', 'Cinder of the Dragon-Cult', "Black ash from the cult's fire rites, still warm in the pouch. "
     "It smells of burnt hair and promises.", 2000, []),
    ('rl_ogre_hide', 'Baerenfell', "Ogre Chief's Hide", "A great slab of grey, warty hide from the chief of the Tallon ogres, thick as a door "
     "and about as pleasant to touch.", 2500, []),
    ('rl_golem_heart', 'zutat_s_edelsteine', 'Golem Heartstone', "The stone that kept Aldessia's guardian moving: a fist of grey crystal "
     "that still twitches toward whoever holds it, waiting for an order.", 3500, []),
]
ITEMS += [
    A('wf_mantle2', 'superrare', 'schultern_nasreddin', 'Silverpelt Mantle', None, None, mods='AUmax +5 MR +2',
      RSBr=1, RSLA=1, RSRA=1, ArBE=0.2, tint=FROST,
      recipe=R('TaBogenbau', 11, [('Armor', 'arm_wp_mantle', 1)], [(RATTEL, 1), (STRIPS, 2)], [], 10)),
    A('wf_mantle3', 'legendary', 'schultern_nasreddin', 'Mantle of the Pack-Mother', None, None, mods='AUmax +10 MR +2 MU +1',
      RSBr=1, RSRu=1, RSLA=2, RSRA=2, ArBE=0.2, tint=FROST,
      recipe=R('TaBogenbau', 14, [('Armor', 'arm_wf_mantle2', 1)], [(MANE, 1), (TINCTURE, 1), (STRIPS, 2)], [], 16)),
    A('rl_sunward_helm', 'superrare', 'helm_verstaerkte_lederruestung', 'Sunward Helm', None, None, mods='MR +2 LEmax +5 AUmax +5',
      RSKo=4, ArBE=0.6, tint=HOLY,
      recipe=R('TaSchmieden', 10, [('Armor', 'arm_tc_helm', 1)], [(SUNSEAL, 1), (GOLD, 1)], [], 10)),
    J('rl_cinder_ward', 'superrare', 'Goldkette', 'Cinder Ward', None, None, mods='AUmax +5', imm='fire', tint=EMBER,
      recipe=R('TaBogenbau', 9, [], [(CINDER, 1), (STRIPS, 1)], [], 8)),
]
_K = {it['key']: it for it in ITEMS}
LOOT_EXTRA += [('loot_unique_Loc03DaVanyaMantraKe', 'Item', SUNSEAL), ('loot_unique_Loc03DaVanyaMantraKe', 'Recipe', 'arm_rezept_rl_sunward_helm'),
               ('loot_unique_wagnitz_drachenkultist_loc03', 'Item', CINDER), ('loot_unique_wagnitz_drachenkultist_loc03', 'Recipe', 'arm_rezept_rl_cinder_ward'),
               ('loot_loc09_kiste_aldessia3', 'Item', TINCTURE), ('loot_loc09_kiste_aldessia3', 'Recipe', 'arm_rezept_wf_mantle3'),
               # Aldessia's lab finally holds an alchemist's stores
               ('loot_loc09_kiste_aldessia1', 'Item', 'zutat_a_drachenblut'), ('loot_loc09_kiste_aldessia2', 'Item', 'zutat_a_diamantstaub'),
               ('loot_loc09_kiste_aldessia3', 'Item', 'zutat_s_edelsteine')]
LOOT_OWN[('NPC', 'Oger_04_kraeftig_loc08_boss')] = [('Item', OGREHIDE, 100, 1), ('Recipe', 'arm_rezept_tw_cuirass', 100, 1)]
LOOT_OWN[('NPC', 'Steingolem_loc09_aldessia')] = [('Item', GOLEMHEART, 100, 1)]
_K['tw_cuirass']['recipe'].update(sellers=[], mats=[(OGREHIDE, 1), (TATZEL, 1), (KOSH, 1)])          # the Ogre Chief carries it
_K['tw_bracers']['recipe']['mats'] = [(GOLEMHEART, 1), (LOUSE, 2), (DWARF_STEEL, 1)]
_K['tw_helm']['recipe']['mats'] = [(CLAW, 2), (DWARF_STEEL, 1)]
for _k in ('wf_mantle2', 'tw_cuirass', 'mh_jerkin', 'mh_breeches', 'mh_grips'): _K[_k]['stage'] = 2
_K['wf_mantle3']['stage'] = 3; _K['rl_sunward_helm']['stage'] = 1; _K['rl_cinder_ward']['stage'] = 1
# the hunter path keeps its mantles, without Survival or Animal Lore
_set('mh_mantle', mods='TaSchleichen +2 MR +1', stats=dict(RSBr=1, RSRu=None, RSLA=1, RSRA=1))
_set('sh_mantle', mods='TaSchleichen +3 TaSinnenschaerfe +2 AW +1', stats=dict(RSBr=1, RSRu=1, RSLA=2, RSRA=2))

# ---------------- B1.5 - B1.7 bonuses ----------------
_set('mh_grips', mods='TaBogen +2 FF +1')
_set('sh_grips', mods='TaBogen +3 FF +1')
_set('tc_bracers', mods='AUmax +5', stats=dict(RSLA=2, RSRA=2))
_set('ts_bracers', mods='AUmax +5 PA +1', stats=dict(RSLA=3, RSRA=3))
_set('tc_cuirass', stats=dict(RSBr=4, RSRu=3, RSBa=3))                    # one step over the vanilla leather cuirass, not three
_set('tc_helm', mods='LEmax +5 AUmax +5', stats=dict(RSKo=3))
_set('ww_robe', mods='AEmax +10 MR +1')
_set('we_robe', mods='AEmax +15 MR +2')
_set('r_hunters_cap', mods='TaTierkunde +2')                               # bought gathering gear: small help only
_set('r_aves_ring', mods='AUmax +5')                                       # a found ring makes nobody a better forager
_set('a_hexknives', name='Hexing Hatchets', base='weapon_crafted_wurfbeil', hit=[('p', 15, [('st', 'ArmHexed')])],
     recipe=dict(consumes=[('Weapon', 'weapon_crafted_wurfbeil', 10)], mats=[(TUSK, 1), ('zutat_a_alkohol', 1)], diff=8))

# ---------------- Batch 2 weapons ----------------
_set('s_tusk', stats=dict(WpW6plus=6))
_set('a_huntress_xbow', hit=[('p', 100, [('dmg', 1, 0, 'physical', '')])])
_set('mh_bow', hit=[('p', 20, [('dmg', 0, 1, 'magic', 'Lightning')])])
_set('a_ember_longbow', stats=dict(WpW6plus=4))
_set('s_thornwood', stats=dict(WpW6=4, WpW6plus=1))
_set('s_nightfang', stats=dict(WpW6plus=5))
_set('m_rf_exile', stats=dict(WpW6plus=7))
# rare finds after the dragon (Heartseeker, Phex's Last Laugh, Wyrmbane) stay strong: the reward for Japhgur

# ---------------- Batch 3: every craftable tells its own story ----------------
DESC = {
 'r_cutlass': "Ferdok's river smugglers keep their cutlasses sharp and their stories blunt. This one has a notch in the guard for every customs man who never found the cargo.",
 'r_ember_hatchet': "The Avestrue miller split his kindling with it, and the wood always caught a little too eagerly. After the third burnt shed his wife made him sell it.",
 'a_ember_saber': "Tulamide fire-steel, folded in the smithies of Khunchom where the forges never cool. The edge glows dull red after every kill, as if remembering home.",
 'a_bloodletter': "A bastard sword with grooves cut along both edges by a field surgeon who hated it. 'Every wound it makes,' he wrote, 'is a wound I cannot close.'",
 'a_firuns_kiss': "Forged in a winter so cold the smith lost two fingers to the anvil. He swore Firun himself breathed on the blade, and the frost on it never quite melts.",
 'a_felling_maul': "Warunk loggers carry hammers like this to drive wedges. Mercenaries noticed that the flanged head drives other things too, mostly knees.",
 'a_kosch_ember_axe': "Quenched in the shrine-fire of an Angrosch temple in the Kosch mountains, where the dwarves say every spark is a prayer. This one prays loudly.",
 'a_thunder_splitter': "A dwarven stonesplitter caught in its own forge when lightning struck the chimney. The smith refused to rework it: 'It has been blessed. Twice.'",
 'a_leech_rapier': "From a duelling school that taught one lesson: let your opponent tire first. The hollow, rune-scratched blade drinks a little strength with every touch.",
 'a_starleech_staff': "A wanderer's staff studded with bits of fallen star by a hedge-mage who could not afford real ones. Each blow pulls a thread of power back to the bearer anyway.",
 'a_ember_longbow': "Resin-soaked yew from the Tallon slopes, cured over a slow fire for a whole winter. Slow to draw, and the arrows leave a trail of sparks.",
 'a_huntress_xbow': "Owlstone's mother built it for hunting from the treeline: a bone stock, a hair trigger and a bolt that arrives a little harder than it should.",
 'a_felling_xbow': "Garethian knights laughed at peasant crossbows until these blunt-nosed bolts began unhorsing them. Now they just do not laugh near peasants.",
 'a_viper_fang': "An Al'Anfan design: venom runs down the fuller and the pommel unscrews to refill it. They call it an embrace because no one notices it until it is too late to let go.",
 'a_thunder_shortsword': "A legionary's short sword etched with a storm-glyph by a Rondra priestess who thought soldiers should hear their blades coming.",
 'a_ironhide_greaves': "Iron greaves weighted with lead along the shin, made for the Ferdok bridge guard. One drunk cannot push a man in these into the river. Two still can.",
 'a_duelist_grips': "A Horasian fencing master's design: heavy leather cuffs that catch a blade on the back of the hand. 'Parry with the steel,' he taught, 'and with the glove when the steel is late.'",
 'a_ironfist': "Combined gauntlets from a Weiden armoury, forged for knights who preferred to hold the line rather than ride at it.",
 'a_iryan_greaves': "Iryan leather is cured in the far south with a resin the Tulamides keep to themselves. Cut to a scout's pattern, these guard the shin and leave the foot free to run and climb.",
 'a_ranger_breeches': "The pattern was pinned inside Grimmzahn's arrow rack, signed by Hagbart, the castle's last ranger. Dark wolf pelt at the knees and sinew in every seam: he swore they outlasted three pairs of boots and one baron.",
 'a_adept_mantle': "Stitched by students of a Punin academy who were tired of iron pauldrons ruining their spells. The astral thread hums faintly when a spell is near.",
 'a_spellweaver_breeches': "Tallon's magician had these embroidered with runes of clear thought after his apprentice set her own sleeve alight mid-spell. The runes do nothing for fire. They do wonders for concentration.",
 'd_gauntlets': "Gauntlets of the old Murolosh kings, refolded with steel that only a dwarf of the royal line may hammer. The fingers close by themselves around a haft.",
 'd_sabatons': "Plated boots made for the hearthguard who stood at the mountain gate for a century. They root their wearer like a stone that has decided not to move.",
 'd_pauldrons': "The pauldrons of the king's hearthguard, each plate engraved with the name of a guard who fell at his post. There is room left for more names.",
 'd_helm': "A storm cap with a single gem over the brow, worn by the watchers of the deep shafts. The gem catches light where no light should be.",
 'k_warboots': "The plated boots of Kurkum, reforged by an Amazon smith to cover the whole leg. 'A sister who cannot be tripped,' she said, 'cannot be beaten.'",
 'w_scale_cuirass': "Scales from the great purple wyrm riveted over plate by smiths who had to work in shifts: the scales stayed hot for a week. Heavy, warm and nearly impenetrable.",
 'w_hide_jerkin': "Flexible scales sewn onto leather soaked in dragon blood. It moves like a second skin, and the skin underneath it never feels the cold again.",
 'w_blood_robe': "A battle-mage's robe steeped in the wyrm's blood, with one scale sewn over the heart. Mages who wear it dream of flying, and wake angry.",
 'w_scale_shield': "Two great wyrm scales bolted to an iron shield. Fire splashes off it like rain; so, now and then, does a sword.",
 'a_hexknives': "Sharpened throwing hatchets, each blade scratched with a curse-rune by a hedge-witch who hated woodcutters. They fly true, and whatever they hit feels the curse before the cut.",
 'a_starfall': "Throwing stars polished with powdered silver by a Tulamide juggler who also happened to be an assassin. In flight they flash like falling stars.",
 'w_witchfire': "Balanced daggers with a hollow core of salamander oil. A witch of the southern marshes made them for a lover who left her. They burn whatever they touch, which seems fair.",
 's_witchfire': "Balanced daggers with a hollow core of salamander oil. A witch of the southern marshes made them for a lover who left her. They burn whatever they touch, which seems fair.",
 'a_spellthief_dirk': "A dirk forged for a thieves' guild that robbed mages. Each cut steals a spark of power, and the guild never once paid for a light.",
 'k_helm': "The Kurkum helmet, reforged with a golden lion crest by an Amazon who had seen the old Queen ride. 'Wear the lion,' she said, 'and remember who it watches.'",
 'h_rh2': "Rhulana's mother's tooth, bound in a mane of braided gold. She stands a little taller wearing it, and nobody mentions it.",
 'h_rh3': "Dwarven gold wrapped around a Kurkum oath. 'Rondra hears every word sworn on this,' says Rhulana, and then she swears quite a lot.",
 'h_rh4': "A wyrm scale set in the Lion Queen's gold. The first Queen of Kurkum wore nothing finer; the songs will say Rhulana wore it better.",
 'h_fo2': "Reforged on a human anvil. Forgrimm grumbles that the work is sloppy, polishes it every evening, and wears it anyway.",
 'h_fo3': "Dwarven steel folded the way Ferolax taught his son, seven times and once more for luck. 'Now that,' says Forgrimm, 'is a ring.'",
 'h_fo4': "Quenched in dragon blood around a sliver of wyrm scale. Ferolax swore to forge this ring and never could. His son did.",
 'h_gw2': "The moon-tree seed has sprouted inside its silver cage. It hums an elven song at dusk that nobody taught it.",
 'h_gw3': "A moon-tree sapling no longer than a finger. Gwendala says it can see in the dark. She is not joking, and that is the unsettling part.",
 'h_gw4': "The moon-tree blossoms around a dragon scale, as in the song of the elven queen who sang the great salamander to sleep. Gwendala knows all the verses now.",
 'h_th2': "The locket has grown into a tiny book on a chain. New pages appear at night, written in your own hand, about things you have not done yet.",
 'h_th3': "Every margin is crowded with notes by every thief who ever owned it. Some of them are spells. One of them is a recipe for very good soup.",
 'h_th4': "Bound in a dragon scale, the grimoire is finally whole, and its last page is blank. It is waiting for you to write it.",
 'm_rf_lion_queen': "Rondra's saber, reforged around a scale of the wyrm. Rhulana held it up to the forge-light and said only: 'Now Kurkum will sing of us.'",
 'm_rf_rondra_verdict': "Sabeth's saber, purified and reforged. The outcast's blade judges for Kurkum now, and it judges harshly.",
 'm_rf_last_oath': "The dragonslayer hammer, finished at last with a scale of the dragon it was sworn against. The oath is kept; the hammer feels lighter for it.",
 'm_rf_exile': "Grimbart's axe, reforged in the forges that once cast him out. Forgrimm brought it home, and the exile's name is spoken in the halls again.",
 'm_rf_sala': "The elven queen's bow, restrung with dragon sinew. Its arrows sing their targets to sleep before the second note.",
 'm_rf_duskarrow': "Faelwen's bow, reborn in Gwendala's hands. It hunts only those who hunt elves now, and it never forgets a face.",
 'm_rf_crimson': "Ravena's dirk, reforged around a wyrm scale. The Circle's oath is yours alone now, and the blade knows it.",
 'm_rf_phex': "The dragon-tooth dagger, stolen from the wyrm twice and finally fitted with a piece of the wyrm itself. Phex is delighted. The wyrm, less so.",
 'wp_mantle': "Iryan leather shoulders lined with the silver ruff of White Fur, the pale wolf-mother of the Avestrue woods. Other wolves smell their old leader on you and hesitate.",
 'wp_jerkin': "Iryan leather faced with dark wolf pelt, cut to the pattern of Grimmzahn's last ranger. Light enough to run in, quiet enough to hunt in.",
 'wp_breeches': "Heavy-duty leather trousers reworked with dark pelt at the knees and belt. They no longer creak, and they remember every trail.",
 'wp_grips': "Iryan leather gloves with a wolf fang set over each knuckle. A steady bow hand, and an unpleasant surprise for anyone who grabs it.",
 'mh_mantle': "A wolf-fur mantle relined with moon-mad pelt. Its silver hairs stand up whenever a spell is cast nearby, and something in the fur turns the spell aside.",
 'mh_jerkin': "A darkwolf jerkin rebuilt around the mane of Greymaw, the mad alpha. Light as ever, and nothing in the woods hears you coming.",
 'mh_breeches': "Darkwolf breeches with moon-mad pelt sewn over the thighs. You hear the twig before you step on it.",
 'mh_grips': "Darkwolf gloves re-stitched with humming moon-sinew. The bow hand never shakes, not even when it should.",
 'mh_bow': "A longbow strung with sinew from the moon-mad pack. When it looses, the string howls, and sometimes the sky answers.",
 'mh_iryan_shoulders': "Iryan shoulder guards with Stormhowl's heartstone sewn under the left plate. The wearer moves a heartbeat ahead of every blow, and spells slide off.",
 'tc_cuirass': "Ferdok's drovers wear tusk-plated leather when they drive the herds past the boar woods. A Count's Town smith made the idea fit for a fight. It creaks, it smells of the field, and it turns a blade.",
 'tc_bracers': "Studded arm guards with a row of tusk tips down each forearm, a drover's trick for keeping angry bulls at arm's length.",
 'tc_helm': "A leather helm with bear claws sewn round the brow, in the old fashion of the Avestrue hunters. It does not make you braver; it makes you harder to kill while you find out.",
 'ts_cuirass': "A tusk cuirass faced with giant-crab shell from the Ferdok harbour. Blades skid off it the way oars skid off a hull.",
 'ts_bracers': "Tusk bracers plated with crab shell at the wrist. They ring like a bell when struck, and the ringing puts duellists off their stroke.",
 'ts_helm': "A clawed helm lined with bitter troll-toad leather and capped with crab shell. Curses taste it and decide to look for someone else.",
 'tw_cuirass': "Crab shell and tusk over the hide of the Tallon ogre-chief, bound with Kosh steel and a linnorm fang over the heart. Its wearer does not fall down. Things fall down around its wearer.",
 'tw_bracers': "Shell bracers reforged around the heartstone of a stone guardian. They still remember how to hold a line that must not break.",
 'tw_helm': "A shell helm under a crest of dwarven steel. Its wearer is always the one the others look to, which is not always a comfort.",
 'ww_robe': "The forest witches spin spider silk with toad sap until the thread stops tangling. Saphira says a robe like this listens to its wearer. She will not say what it answers.",
 'ww_hood': "A pointed hat stiffened with spider silk in the witches' way. Whatever it hears, it whispers to you, mostly gossip.",
 'ww_shoes': "Soft shoes soled with silk and a warm firefly sac in each heel. The witches wear them to dance in the woods without leaving a trace.",
 'we_robe': "A witch-robe threaded with glowing firefly silk and a glittering green eye at the collar. Tallon's magician helped with the stitching, and the robe will not burn.",
 'we_hood': "A witch's hat with a glittering green eye set over the brim. It sees spells coming a moment before you do.",
 'we_shoes': "Witch slippers with ember-sac soles that never cool. Light steps, warm feet, quick hands: the old Tallon recipe for a long night.",
 'sh_mantle': "A moonhowl mantle fringed with harpy feathers from the Tallon cliffs. It catches the wind, and arrows that should hit you catch nothing.",
 'sh_grips': "Moonhowl gloves with a bear claw over the draw finger and harpy down in the palm. The string leaves the hand as softly as a sigh.",
 'sh_hood': "A leather hood crested with harpy feathers. You see the hawk before the hawk sees you.",
 'wf_mantle2': "The White Fur mantle, relined with the pelt of Duskmane, old lord of the Rattelshof pack. It is warmer now, and heavier with two wolves' worth of pride.",
 'wf_mantle3': "Three wolves' furs bound with Aldessia's silver tincture and the mane of the mad alpha. Wolves bow their heads to whoever wears it, and men find they would rather not try.",
 'rl_sunward_helm': "A clawed helm crowned with the Grand Inquisitor's own seal. Magic slides off it the way his sermons slid off the witches of the Dark Forest.",
 'rl_cinder_ward': "A pinch of the dragon-cult's sacred cinder sealed in a gold locket. The fire that answered their prayers does not answer anyone's against you.",
 's_rondra_reprimand': "A Kurkum saber reforged with dwarven steel and gold leaf. It punishes cowardice and rewards the warrior who presses on.",
 's_mountain_patience': "A dwarven maul reworked from a woodsman's hammer with steel from the deep forges. The mountain waits, and then it falls on you.",
 's_nightsong': "A quick elven bow restrung with elf wood and fine sinew. At night its string hums a lullaby, and the creatures of the forest listen.",
 'd_black_widow': "A twin-tipped dirk regrown around two green spider eyes. Her first bite weakens; her second bite kills.",
}
for _k, _d in DESC.items():
    if _k in _K: _K[_k]['flavor'] = _d
_set('mh_breeches', stats=dict(RSBa=1, RSLB=3, RSRB=3))   # Tallon: 7 like the Ranger's Breeches; the bonuses are the difference

# throwing weapons: one craft makes 25, same ingredients (player, 2 Nov); vanilla throwing plans get the same in build_remastered.py
for _k in ('a_hexknives', 'a_starfall', 's_witchfire'): _K[_k]['batch'] = 25
# ... and weigh a tenth of their base (player, 2 Nov)
for _k, _g in (('a_hexknives', 80), ('a_starfall', 10), ('s_witchfire', 30), ('r_balanced_knives', 30), ('r_felling_hatchets', 80)): _K[_k]['stats']['Gew'] = _g
# Avestrue Gambeson: chest 3, belly 2, back 2 (player, 2 Nov); vanilla's padded tunic is already 2/2/2, so early cloth caps at 9
_set('r_gambeson', stats=dict(RSBr=3, RSRu=2, RSBa=2))
# Harbour Riposte (player, 2 Nov): Jorgo comes before the Dark Forest, so his rapier stays under Farfara's magic rapier (1W6+5, AT +1):
# a plain rapier's damage, a parry edge and one trick
_set('s_riposte', hit=[('p', 15, [('st', 'ArmSundered')])], stats=dict(WpW6plus=4, WpATmod=0, WpPAmod=1))
