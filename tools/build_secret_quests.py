"""Drakensang TDE - Remastered: secret quests (installs AFTER armory_v2 and remastered_systems; uses their items).

1. The Crimson Circle (starts outside the Golden Lance tavern, Count's Town, after Moorbridge): seven rogue duelists placed from Ferdok harbour to behind
   the Fire Falls. Humans with legendary gear who drop it. Rhulana, Gwendala and Forgrimm each meet a personal rival.
2. The Codex of Hidden Fire (Rakorium in the Ferdok house, all chapters): four torn codex pages in dungeons, a reward per page,
   and a finale in which Rakorium reads the codex aloud. Nothing goes wrong. Almost.
3. Wendelin Raunefuss, teller of rumours (Wagoner's Home, Ferdok): free hints to every secret in the pack.
Usage: python -I tools/build_secret_quests.py "<game>/export/db/armory_backup" mods/secret_quests
"""
import sys, os, shutil, sqlite3, tempfile, math
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod
from quests import Story, ACTSEL as A
from armory_data import DUELIST_PIECES

db, out = sys.argv[1], sys.argv[2]
ROOT = os.path.join(os.path.dirname(__file__), '..')
m = Mod(db, 'secretquests'); st = Story(m, 'secretquests')

# templates of the earlier modules (armory_v2, remastered_systems): a scratch copy of static.db4 with their SQL applied
snap = tempfile.mkdtemp()
shutil.copy2(os.path.join(db, 'static.db4'), snap)
sc = sqlite3.connect(os.path.join(snap, 'static.db4')); sc.text_factory = lambda b: b.decode('cp1252', 'replace'); sc.row_factory = sqlite3.Row
for mod in ('armory_v2', 'remastered_systems'):
    sc.executescript(open(os.path.join(ROOT, 'mods', mod, 'sql', 'static.sql'), encoding='cp1252').read())
st.templates_from = sc
def cat(iid):
    own = next((ty for ty, i, _ in m.templates if i == iid), None)
    if own: return own
    for t in ('Weapon', 'Armor', 'Shield', 'Jewelry', 'Item', 'Ammo'):
        if sc.execute(f'select 1 from _Template_{t} where Id=?', (iid,)).fetchone(): return t
    raise KeyError(iid)

TA = lambda did, take: f'TalkedAbout dialogId="{did}" takeId="{take}"; '
QOPEN = lambda q: f'IsQuestUnLocked quest="{q}"; '
QDONE = lambda q: f'IsQuestClosed quest="{q}"; '
TDONE = lambda t, q: f'IsTaskClosed task="{t}" quest="{q}"; '
HAS = lambda iid, n: f'HasAmount category="{cat(iid) if not iid.startswith("arm_q_") else "Item"}" templateId="{iid}" operator="greaterOrEqual" count="{n}"; '
INV = lambda iid: f'IsInInventory category="Item" templateId="{iid}"; '
PARTY = lambda who: f'IsPartyMember who="{who}"; '
GIVE = lambda iid, n=1: f'CreateEntity category="{cat(iid)}" templateId="{iid}" how="spawnInStorage" entity="Hero" number="{n}" executeAfter="true" {A}'
GOLD = lambda ducats: f'GiveGold amount="{ducats * 100}" executeAfter="true" {A}'
TAKE = lambda to, iid, n: (f'DestroyEntity category="Item" templateId="{iid}" count="{n}" storageGroup="PlayerParty" executeAfter="true" '
                           f'notInStorage="false" destroyDirectly="false" {A}')   # handed-in items are gone (no resale)
XP = lambda n: f'GiveQuestXp questXp="{n}" {A}'
RHULANA, FORGRIMM, GWENDALA = 'Rhulana', 'Forgrimm_Sohn_des_Ferolax', 'pc_gwendala'

# ---------------- quest items (made here; vanilla icons) ----------------
from dsa import make_icon
os.makedirs(os.path.join(out, 'icons'), exist_ok=True); ICONS = []
def qitem(iid, base, name, desc, stack=1, art=None, quest='NONE', robable=0):
    key = art or iid[4:]                       # own icon file so Codex art can replace it mid-game
    custom = os.path.join(ROOT, 'assets', 'remastered_icons', f'arm_{key}.dds')
    dst = os.path.join(out, 'icons', f'arm_{key}.dds')
    if os.path.isfile(custom): shutil.copy2(custom, dst)       # always ship the newest art
    elif not os.path.isfile(dst):
        brush = m.s.execute('select IconBrush from _Template_Item where Id=?', (base,)).fetchone()[0]
        make_icon(os.path.join(ROOT, 'tools', 'research', 'out', 'icons_vanilla', brush.split('/')[-1] + '.dds'), dst, 'regular')
    if f'arm_{key}.dds' not in ICONS: ICONS.append(f'arm_{key}.dds')
    m.template('Item', base, iid, name, desc, Value=0, MaxStackCount=stack, StackCount=1, Robable=robable, QuestId=quest, CanDestroy=0, IconBrush=f'icons/arm_{key}')   # quest item (audit A6)
qitem('arm_q_sigil', 'robable_glueksbringer', 'Crimson Sigil', quest='arm_q_crimson', desc=
      'A red iron seal worn by the duelists of the Crimson Circle. Master Klingenhand, outside the Golden Lance in Ferdok, wants them all.', stack=7)
qitem('arm_q_ledger', 'loc02_lieferschein', "Klingenhand's Ledger", quest='arm_q_crimson', desc=
      "Seven names in a shaking hand:\\n"
      "Jorgo Fairwind, the Harbour Riposte: drinks where Ardo fell, in Ferdok harbour.\\n"
      "Ilgrim Ashblade: burned a chapel. Smells of ash, fond of ruins.\\n"
      "Faelwen Duskarrow: an elf who hunts elves. Likes old trees and wet feet.\\n"
      "Sir Wolfhart the Oathbreaker: sold a castle gate. Keeps company with the dead.\\n"
      "Sabeth Lionsbane: an outcast Amazon. Hunts something with fangs, far from here.\\n"
      "Grimbart Ironbeard: a banished dwarf. Guards something deep under the mountains.\\n"
      "Ravena Blutfeder, the Crimson Master: waits where fire meets stone. You will know it when you get there.")
PAGES = [  # page id, name, chest (Id, level), hint
    ('arm_q_page1', 'Codex Page I: Of Embers', ('jischka_tot_liegend', 'dungeon02_kanalisation'), 'in the sewers under Ferdok'),
    ('arm_q_page2', 'Codex Page II: Of Ashes', ('loc03_truhe_burg', 'location03'), 'in a locked chest by the ruins of the Blood Mountains'),
    ('arm_q_page3', 'Codex Page III: Of Bones', ('loc04_sarkophag_chest_1', 'dungeon04_gruft'), 'where the dead are buried with their secrets'),
    ('arm_q_page4', 'Codex Page IV: Of Dreams', ('skelett_tot_sitzend_loc05', 'dungeon05_burg'), 'in the vaults of an old castle'),
]
for pid, name, (chest, lvl), hint in PAGES:
    qitem(pid, 'loc02_lieferschein', name, art='q_page', quest='arm_q_codex', desc='A scorched page in draconic script. Master Rakorium will want it.')
    m.place('Item', pid, 'chest', chest, lvl)

# ================= 1. THE CRIMSON CIRCLE =================
Q = 'arm_q_crimson'
FENCE = 'MeleeAttack 6.0 0, Finte 3.0 0, GezielterStich 2.0 0, Todesstoss 1.0 0'
HEAVY = 'MeleeAttack 6.0 0, Wuchtschlag 3.0 0, Niederwerfen 2.0 0, Hammerschlag 1.0 0'
SABER = 'MeleeAttack 6.0 0, Finte 2.0 0, Klingensturm 2.0 0, Wuchtschlag 1.0 0'
# Every human boss and crew fights with the full set its weapon allows (player, 3 Nov), casts Armatrutz on drawing, and brings a mage.
# the strongest moves lead (player, 3 Nov): Stormblade, Mortal Blow, Roundhouse Blow, Strike of Wrath, where the weapon allows them
MOVESET = {'TaDolche': 'MeleeAttack 2.0 0, Klingensturm 3.0 0, Todesstoss 3.0 0, GezielterStich 2.0 0, Finte 1.0 0',
           'TaFechtwaffen': 'MeleeAttack 2.0 0, Klingensturm 3.0 0, Todesstoss 3.0 0, GezielterStich 2.0 0, Finte 1.0 0',
           'TaSaebel': 'MeleeAttack 2.0 0, Klingensturm 4.0 0, Befreiungsschlag 3.0 0, Wuchtschlag 1.0 0, Niederwerfen 1.0 0',
           'TaSchwerter': 'MeleeAttack 2.0 0, Klingensturm 3.0 0, Befreiungsschlag 3.0 0, GezielterStich 1.0 0, Wuchtschlag 1.0 0',
           'TaSpeere': 'MeleeAttack 2.0 0, Todesstoss 3.0 0, GezielterStich 2.0 0, Umreissen 1.0 0, Finte 1.0 0',
           'TaZwHiebwaffen': 'MeleeAttack 2.0 0, Hammerschlag 3.0 0, Befreiungsschlag 3.0 0, Niederwerfen 1.0 0, Wuchtschlag 1.0 0',
           'TaHiebwaffen': 'MeleeAttack 2.0 0, Hammerschlag 3.0 0, Befreiungsschlag 3.0 0, Niederwerfen 1.0 0, Wuchtschlag 1.0 0'}
def moves(wid):
    r = sc.execute('select TaAttr from _Template_Weapon where Id=?', (wid,)).fetchone()
    return MOVESET.get(r[0] if r else '', MOVESET['TaFechtwaffen'])
HEXER = dict(AEmax=120, AE=120, ZaIgnifaxius=12, ZaFulminictus=12, ZaPlumbumbarum=10, ZaSomnigravis=10, ZaHorriphobus=10, ZaArmatrutz=10,
             Behaviour='cast_always')   # no Paralysis: being turned to stone is no fun (player, 3 Nov)
ARMATRUTZ = lambda who: f'CastSpell who="{who}" spellId="Armatrutz" target="{who}" zfpUnused="12" executeAfter="true" {A}'
def stats(le, at, pa, rs, mr, att, xp, lvl, fk=0, aw=8):
    s = dict(LE=le, LEmax=le, LEmin=-10, AT=at, PA=pa, AW=aw, MR=mr, BasisXP=xp, Stufe=lvl, Behaviour='clever_fighter', ScriptPreset='', SetupEquipment='',
             **{k: rs for k in ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')}, **dict(zip(('MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK'), att)))
    if fk: s['FK'] = fk
    return s
DUELISTS = [  # key, display, clone, level, anchor, offset, gear [(id, lootable)], stats, attacks, melee?, companion, greeting, companion line, taunt, quest xp, task title, hint
    ('jorgo', 'Jorgo Fairwind, the Harbour Riposte', 'Stoerrebrand_Abwerber', 'location02_hafen', ('MarkerPoint', 'loc02_tatort_ardo'), (3.0, 0, 0),
     [('arm_s_riposte', 1)], stats(120, 17, 15, 3, 5, (14, 12, 13, 12, 15, 16, 14, 14), 15, 8), FENCE, True, None,
     "You have the look of someone counting the steps between us. Seven, by my count. I am Jorgo Fairwind, first blade of the Crimson Circle, and I never attack first.",
     None, "Then you will die second. En garde!", 30, 'Jorgo Fairwind', "Jorgo Fairwind drinks in Ferdok harbour, near the spot where Ardo was found."),
    ('ilgrim', 'Ilgrim Ashblade', 'loc02_roter_schlaechter_01', 'location03', ('MarkerPoint', 'Loc03_Marker_Burg'), (2.5, 0, 0),
     [('arm_s_ashblade', 1)], stats(150, 18, 14, 4, 6, (15, 12, 12, 10, 14, 15, 15, 16), 18, 10), SABER, True, None,
     "Smell that? Ash. I burned a chapel of Praios with the priests inside, and the Circle paid me in gold for it. Klingenhand sent you, didn't he.",
     None, "Then let us see if you burn as well as they did!", 40, 'Ilgrim Ashblade', "Ilgrim Ashblade smells of ash and is fond of ruins. The ledger says no more."),
    ('faelwen', 'Faelwen Duskarrow, Hunter of Elves', 'loc02_elfentrainer', 'location03', ('MarkerPoint', 'loc03_marker_raeuber_danos_goto'), (2.5, 0, 1.0),   # Moorbridge closes for good (player, 2 Nov)
     [('arm_l_duskarrow', 1)], stats(150, 15, 12, 3, 9, (14, 13, 16, 12, 17, 17, 13, 13), 20, 11, fk=20, aw=10), 'Meisterschuetze 1.0 0', False, GWENDALA,   # Master Marksman only (3 Nov)
     "Quiet, now. I have been listening to you crash through this forest for an hour. Elves pay well to have other elves found. Humans pay better to have them lost.",
     "Faelwen. Kin-slayer. The forest still sings the names of those you sold. Today it learns a new verse: yours.",
     "Run, then. I like it better when they run.", 50, 'Faelwen Duskarrow', "Faelwen Duskarrow, an elf who hunts elves, likes old trees and wet feet. He fights with a bow."),
    ('wolfhart', 'Sir Wolfhart the Oathbreaker', 'Gundwein_L01', 'location08', ('MarkerPoint', 'Mapmarker_loc08_Tallon_Gruft'), (3.0, 0, 0),   # Grimmzahn closes for good (player, 2 Nov)
     [('arm_l_oathbreaker', 1), ('arm_s_oath_pavise', 1)], stats(220, 19, 17, 6, 7, (16, 12, 12, 13, 13, 14, 17, 18), 22, 13), HEAVY, True, None,
     "The dead in this crypt keep better company than the living. I served Grimmzahn, once. I swore on my sword to hold the gate. Then the orcs offered more than the Baron did.",
     None, "Klingenhand's errand-runner. Come, then. I have broken better oaths than you.", 60, 'Sir Wolfhart the Oathbreaker',
     "Sir Wolfhart the Oathbreaker keeps company with the dead. Sword and shield."),
    ('sabeth', 'Sabeth Lionsbane, the Outcast', 'loc02_amazon_anfuehrerin', 'location08', ('MarkerPoint', 'loc08_questmarker_tatzelwurm_hoehle'), (3.0, 0, 0),
     [('arm_l_lionsbane', 1)], stats(240, 20, 16, 5, 8, (17, 12, 13, 12, 14, 16, 16, 16), 24, 14), SABER, True, RHULANA,
     "I hunt the tatzelwurm for its fangs, and the Circle for its gold. Kurkum took my name, my sisters and my lion. It did not take my sword arm.",
     "Sabeth. You killed a sister in a duel of honour and called it justice. Kurkum was merciful to let you leave. Rondra will not be.",
     "Then come, both of you. Rondra loves a good fight.", 70, 'Sabeth Lionsbane', "Sabeth Lionsbane, an outcast Amazon, hunts something with fangs, far from Ferdok."),
    ('grimbart', 'Grimbart Ironbeard, the Exile', 'Loc09_Drachentoeter_02', 'location10', ('MarkerPoint', 'loc10_marker_teleporter'), (2.5, 0, 0),
     [('arm_l_exile_cleaver', 1)], stats(300, 20, 17, 7, 9, (17, 12, 12, 10, 13, 13, 18, 19), 26, 16), HEAVY, True, FORGRIMM,
     "Turn around, longlegs. The Deeps are no place for you. Murolosh cast me out for what I did with this axe, and I have guarded these halls alone ever since.",
     "Grimbart Ironbeard. My father spoke your name once, then spat in the fire. Pick up your cleaver, exile. Angrosch is watching.",
     "A son of Ferolax! Hah! Then I will make it quick, for your father's sake.", 80, 'Grimbart Ironbeard',
     "Grimbart Ironbeard, a banished dwarf, guards something deep under the mountains."),
    ('ravena', 'Ravena Blutfeder, the Crimson Master', 'loc02_trainer_praios_magie', 'location11', ('MarkerPoint', 'marker_feuerbruecke01'), (3.0, 0, 0),
     [('arm_m_crimson_vow', 1)], stats(450, 23, 19, 7, 12, (18, 15, 15, 14, 17, 18, 17, 17), 30, 18), FENCE, True, None,
     "So the old man's dog has come all this way. You have killed my six best students. I taught every one of them, and I was holding back.",
     None, "Fire behind me, stone beneath you. Let us finish this.", 100, 'Ravena Blutfeder, the Crimson Master',
     "Ravena Blutfeder, the Crimson Master, waits where fire meets stone."),
]
PURSE = dict(jorgo=12, ilgrim=16, faelwen=20, wolfhart=35, sabeth=40, grimbart=20, ravena=20)   # ducats; gold where it can still be spent (audit C1)
# Each duelist is the hardest human fight of their area (player, 2 Nov): more life, better attack and parry, spells for the casters,
# an aura for the ash-burner, and two bodyguards who draw with them (Grimbart guards the Deeps alone, as his greeting says).
FIERCE_CC = {'ilgrim': dict(AuraStatuseffect='burning'),
             'faelwen': dict(AEmax=90, AE=90, ZaFulminictus=12, ZaArmatrutz=12),   # an elven hunter: lightning and Armatrutz (player, 2 Nov)
             'ravena': dict(AEmax=150, AE=150, ZaIgnifaxius=14, ZaPlumbumbarum=12, ZaHorriphobus=10, ZaSomnigravis=10, ZaKulminatio=12)}
GUARDS = {  # key -> (name, clone NPC, weapon, stats, attacks)
    'jorgo': ('Harbour Bravo', 'Raeuber01_loc02_mr_pickpocket', 'Rapier', stats(110, 15, 13, 2, 4, (13, 11, 12, 10, 13, 14, 13, 13), 8, 7), FENCE),
    'ilgrim': ('Ash Brother', 'loc02_roter_schlaechter_01', 'Saebel', stats(130, 16, 12, 3, 5, (14, 10, 11, 9, 12, 13, 14, 15), 9, 8), SABER),
    'faelwen': ('Elf-Tracker', 'Raeuber03_loc02_milde_gabe_dieb_2', 'Speer', stats(130, 15, 12, 3, 6, (13, 11, 14, 10, 14, 15, 13, 13), 10, 9), 'MeleeAttack 6.0 0, Umreissen 2.0 0'),
    'wolfhart': ('Grimmzahn Deserter', 'soldat_ferdok_04_loc02_trainer_praios_nahkampf', 'Langschwert', stats(170, 17, 14, 5, 6, (14, 10, 11, 10, 12, 13, 15, 16), 11, 11), HEAVY),
    'sabeth': ('Outcast Amazon', 'loc02_amazon_anfuehrerin', 'Amazonensaebel', stats(180, 18, 14, 4, 6, (15, 11, 12, 11, 13, 15, 15, 15), 12, 12), SABER),
    'ravena': ('Crimson Adept', 'loc02_trainer_praios_magie', 'Magierrapier', dict(stats(200, 18, 15, 4, 12, (15, 15, 14, 13, 15, 15, 14, 13), 14, 14),
              AEmax=80, AE=80, ZaIgnifaxius=10, ZaFulminictus=8), FENCE),
}
HEXERS = ('jorgo', 'ilgrim', 'faelwen', 'wolfhart', 'sabeth')   # Ravena's guards are mages already; Grimbart fights alone
GUARD_IDS = lambda key: ([f'arm_npc_cc_{key}_g{i}' for i in (1, 2)] if key in GUARDS else []) + ([f'arm_npc_cc_{key}_g3'] if key in HEXERS else [])
lt_guard = st.loot_table('arm_lt_cc_guard', [('Money', 'Geld', 100, 600, 1), ('Item', 'zutat_s_edelsteine', 30, 1, 1)])
for key, disp, clone, lvl, anchor, off, gear, sts, attacks, melee, comp, greet, comp_line, taunt, qxp, ttl, hint in DUELISTS:
    nid, did = f'arm_npc_cc_{key}', f'arm_dlg_cc_{key}'
    sts = dict(sts, LE=int(sts['LE'] * 1.6), LEmax=int(sts['LEmax'] * 1.6), AT=sts['AT'] + 2, PA=sts['PA'] + 2, IsVictoryWorthy=1, **FIERCE_CC.get(key, {}))
    if key in GUARDS:
        gname, gclone, gweap, gsts, gatt = GUARDS[key]
        for i, gid in enumerate(GUARD_IDS(key)):
            if gid.endswith('_g3'):   # the group's mage, a step behind
                st.npc(gid, 'Crimson Hexer', 'loc02_trainer_praios_magie', lvl, anchor, (off[0], off[1] + 1.0, off[2] - 2.5), park=True,
                       SpecialAttackChances=MOVESET['TaFechtwaffen'], LootTable=lt_guard, **dict(gsts, **HEXER))
                st.stock(gid, 'Weapon', 'Magierrapier', lootable=1)
                continue
            st.npc(gid, gname, gclone, lvl, anchor, (off[0] + (-1.8 if i else 1.8), off[1] + 1.0, off[2] + 2.0), park=True, SpecialAttackChances=moves(gweap),   # 1 m up (3 Nov)
                   LootTable=lt_guard, **gsts)
            st.stock(gid, 'Weapon', gweap, lootable=1)
    _pc = DUELIST_PIECES.get(key, []); _pc = [_pc] if isinstance(_pc, str) else _pc
    piece = [('Armor', x, 100, 1, 1) for x in _pc]   # heirloom-set pieces (armory v2.4/2.5)
    extra = [('Ammo', 'arm_am_duskfeather', 100, 20, 1), ('Recipe', 'arm_rezept_am_duskfeather', 100, 1, 0)] if key == 'faelwen' else []   # his own arrows and their plan
    lt = st.loot_table(f'arm_lt_cc_{key}', [('Money', 'Geld', 100, PURSE[key] * 100, 1), ('Item', 'zutat_s_edelsteine', 60, 2, 1), ('Item', 'zutat_s_blattgold', 50, 1, 1)] + piece + extra)
    if melee: attacks = moves(gear[0][0])   # the full set of the duelist's own weapon
    st.npc(nid, disp, clone, lvl, anchor, off, park=True, SpecialAttackChances=attacks, LootTable=lt, **sts)   # parked until Klingenhand's job (after Moorbridge)
    for iid, loot in gear: st.stock(nid, cat(iid), iid, lootable=loot)
    st.stock(nid, 'Item', 'arm_q_sigil', lootable=1)
    # Faelwen carries no arrows (3 Nov he had 40 unlootable Duskfeathers and neither his dropped arrows nor the plan reached the
    # player, 6 Nov): vanilla archers carry none either and shoot anyway, and their loot table alone drops their ammo.
    draw = f'SetFaction faction="FaFeind" who="{nid}" executeAfter="true" {A}' + (f'EquipBestCloseRangeWeapon who="{nid}" executeAfter="true" {A}' if melee else '')
    draw += ''.join(f'SetFaction faction="FaFeind" who="{g}" executeAfter="true" {A}EquipBestCloseRangeWeapon who="{g}" executeAfter="true" {A}' for g in GUARD_IDS(key))
    draw += ''.join(ARMATRUTZ(x) for x in [nid] + GUARD_IDS(key))   # everyone hardens up as they draw
    if key == 'faelwen':   # he calls two nature-spirit bears of the Dark Forest, one at each side, 5 m out (not on his head, 3 Nov)
        for _j, _dx in ((1, 5.0), (2, -5.0)):
            _pt = st.point(f'arm_npc_cc_faelwen_bear{_j}_entry', lvl, anchor, (off[0] + _dx, off[1] + 1.0, off[2] + 2.0))
            draw += f'CreateEntity category="Monster" templateId="Baer_naturgeist" how="spawnAtEntity" entity="{_pt}" number="1" executeAfter="true" {A}'
    fight = ['r_fight', 'r_bye']
    takes = [dict(id='StartState', type='StartState', kids=(['t_greet_c'] if comp else []) + ['t_greet']),
             dict(id='t_greet', type='Take', kids=fight, text=greet),
             dict(id='r_fight', type='Response', kids=['t_draw'], text='Your Circle ends here. Draw.'),
             dict(id='t_draw', type='Take', act=draw, text=taunt),
             dict(id='r_bye', type='Response', text='Not today.')]
    if comp:
        takes += [dict(id='t_greet_c', type='Take', cond=[PARTY(comp)], kids=['r_next'], text=greet),
                  dict(id='r_next', type='Response', kids=['t_comp'], text='<Next>'),
                  dict(id='t_comp', type='Take', speaker=comp, kids=fight, text=comp_line)]
    st.dialog(did, nid, takes)
    st.task(f'{Q}_{key}', ttl, hint, f'{disp.split(",")[0]} is dead. Their sigil belongs to Master Klingenhand.', parent=Q, state='unlocked',
            close_cond=[f'IsDead who="{nid}"; '], close_act=XP(qxp), target=nid)

# Master Alrik Klingenhand: outside the Golden Lance in the Count's Town (the tavern itself opens only with Rhulana's quest), and later Murolosh (he follows the last of the Circle; audit A10).
# Both share one quest line (Or-conditions over both dialogs), like the travelling Ulfried.
MASTER, MD = 'arm_npc_klingenhand', 'arm_dlg_klingenhand'
KSPOTS = {MD: (MASTER, 'location02_grafenstadt', ('Entry', 'loc02_entry_lanze_graf'), (2.5, 0, 1.0),
               "Hm? You have a fighter's hands and a fighter's eyes. Sit, if you like. Alrik Klingenhand: once the finest blade in Ferdok, "
               "now the finest drinker outside the Golden Lance. They keep the bench warm for me."),
          'arm_dlg_klingenhand_m': ('arm_npc_klingenhand_m', 'location09', ('NPC', 'Loc09_Zwergenhaendler'), (-2.5, 0, -1.5),
               "You found me! I could not sit in Ferdok while you hunted my students across the world. The dwarves serve a fine dark beer. Sit.")}
KD = list(KSPOTS)
KANY = lambda take: [TA(d, take) for d in KD]
KNONE = lambda take: ['!' + TA(d, take) for d in KD]
SABETH_DEAD = 'IsDead who="arm_npc_cc_sabeth"; '
AFTER_MOORBRIDGE = QDONE('loc04_mainquest')   # review 1 Nov: the Circle (and its gear) only after you are back from Moorbridge
HAS_ITEM = lambda cat, iid: f'HasAmount category="{cat}" templateId="{iid}" operator="greaterOrEqual" count="1"; '
DESTROY = lambda cat, iid: (f'DestroyEntity category="{cat}" templateId="{iid}" count="1" storageGroup="PlayerParty" executeAfter="true" '
                            f'notInStorage="false" destroyDirectly="false" {A}')
for did, (nid, lvl, anchor, off, hello) in KSPOTS.items():
    st.npc(nid, 'Alrik Klingenhand, Retired Fencing Master', 'staedter_reich_m_01_loc02_haendler_graf_waffen', lvl, anchor, off, ScriptPreset='',
           turn=180 if lvl == 'location02_grafenstadt' else 0)   # at the Golden Lance he faced the wall (player, 2 Nov)
    HUB = ['r_early', 'r_story', 'r_where', 'r_sig3', 'r_sig7', 'r_sabeth', 'r_bye']
    st.dialog(did, nid, [
        dict(id='StartState', type='StartState', kids=['t_return', 't_first']),
        dict(id='t_first', type='Take', kids=HUB, text=hello),
        dict(id='t_return', type='Take', kids=HUB, cond=[TA(did, 't_first')], text="Ah, my young blade. Sit, sit. What news?"),
        dict(id='r_early', type='Response', kids=['t_early'], cond=KNONE('r_accept') + ['!' + AFTER_MOORBRIDGE], text='You look like a man with a story.'),
        dict(id='t_early', type='Take', kids=HUB, text="A story? Perhaps. Not for someone who has only seen Ferdok, though. Go and see a little of the world, "
             "and come back when your boots are muddier."),
        dict(id='r_story', type='Response', kids=['t_story'], cond=KNONE('r_accept') + [AFTER_MOORBRIDGE], text='You look like a man with a story.'),
        dict(id='t_story', type='Take', kids=['r_accept', 'r_bye'],
             text="Seven students. The best I ever had. They called themselves the Crimson Circle, swore an oath in blood on a red dirk, and sold their "
                  "swords to anyone who paid. My son challenged them to a friendly bout. It was not friendly. I am too old to hunt them. You are not. "
                  "Each of them wears a red iron sigil. Bring me all seven, and I will give you what I gave none of them: everything I know."),
        dict(id='r_accept', type='Response', kids=['t_accepted'], text='I will break the Crimson Circle.'),
        dict(id='t_accepted', type='Take', kids=['r_bye'], act=GIVE('arm_q_ledger') + ''.join(st.arrive(x) for d in DUELISTS for x in [f'arm_npc_cc_{d[0]}'] + GUARD_IDS(d[0])),
             text="Then take my ledger; it holds all I have heard of them. Start with Jorgo. He drinks in the harbour, where poor Ardo fell. "
                  "And mind Ravena, the last of them. I taught her everything, and she taught herself the rest."),
        dict(id='r_where', type='Response', kids=['t_where'], cond=[KANY('r_accept')] + KNONE('t_sig7'), text='Remind me where they are.'),
        dict(id='t_where', type='Take', kids=HUB,
             text="Jorgo drinks in the harbour. For the rest I only have scraps: ash and ruins, old trees and wet feet, the company of the dead, "
                  "fangs far from here, something deep under the mountains, and fire meeting stone. It is all in the ledger. Your road will take you "
                  "to them, I think. And if I am not here, I will have followed you."),
        dict(id='r_sig3', type='Response', kids=['t_sig3'], cond=[HAS('arm_q_sigil', 3)] + KNONE('t_sig3'), text='I have three of their sigils.'),
        dict(id='t_sig3', type='Take', kids=HUB, act=GIVE('arm_a_klingenhand_gloves') + GOLD(80),
             text="Three! By Rondra, three. Here: my old fencing gloves. Forty duels and not one lost while I wore them. Keep the sigils; bring me all seven."),
        dict(id='r_sig7', type='Response', kids=['t_sig7'], cond=[HAS('arm_q_sigil', 7)] + KNONE('t_sig7'), text='All seven sigils. The Circle is broken.'),
        dict(id='t_sig7', type='Take', kids=['r_bye'], act=TAKE(nid, 'arm_q_sigil', 7) + GIVE('arm_j_crimson_circle') + GOLD(100),
             text="Seven. Ravena too? Then my son can rest. This ring was mine, when I was the best duelist in the Middenrealm. "
                  "Wear it. From today, the best is you."),
        # audit N5: Rhulana's choice about Sabeth: keep Lionsbane (and its reforge into Rondra's Verdict), or lay it down in her honour
        dict(id='r_sabeth', type='Response', kids=['t_sabeth'],
             cond=[SABETH_DEAD, PARTY(RHULANA), HAS_ITEM('Weapon', 'arm_l_lionsbane'), HAS_ITEM('Jewelry', 'arm_h_rh1')] + KNONE('t_sabeth_honour') + KNONE('t_sabeth_keep'),
             text='Sabeth is dead. Rhulana has something to say about her saber.'),
        dict(id='t_sabeth', type='Take', kids=['r_sabeth_next'], text="Sabeth Lionsbane. She was the best of them, and the saddest. Go on, Amazon. Say it."),
        dict(id='r_sabeth_next', type='Response', kids=['t_sabeth_rhulana'], text='<Next>'),
        dict(id='t_sabeth_rhulana', type='Take', speaker=RHULANA, kids=['r_sabeth_honour', 'r_sabeth_keep'],
             text="She was Kurkum once. Her saber should not be swung by strangers, nor sold. Let me lay it down for her, and Rondra will remember the "
                  "gift. Or keep it, and make it something greater. It is your choice, not mine."),
        dict(id='r_sabeth_honour', type='Response', kids=['t_sabeth_honour'], text='Lay Lionsbane down for her, Rhulana.'),
        dict(id='t_sabeth_honour', type='Take', kids=['r_bye'], act=DESTROY('Weapon', 'arm_l_lionsbane') + DESTROY('Jewelry', 'arm_h_rh1') + GIVE('arm_h_rh2') + XP(50),
             text="Klingenhand bows his head. Rhulana lays the saber across her mother's tooth, and when she lifts the tooth again it is bound in braided "
                  "gold: the Mane of the Lioness, blessed by the dead. Rondra takes her due."),
        dict(id='r_sabeth_keep', type='Response', kids=['t_sabeth_keep'], text='We keep it. Sabeth would have wanted it used.'),
        dict(id='t_sabeth_keep', type='Take', kids=HUB, text="Then use it well. A saber remembers who carried it."),
        dict(id='r_bye', type='Response', text='Farewell, Master Klingenhand.'),
    ])
st.task(Q, 'The Crimson Circle', "Master Alrik Klingenhand, outside the Golden Lance in Ferdok, asked me to hunt down the seven duelists of the Crimson Circle "
        "and bring him their sigils. His ledger has a hint for each. He says he may follow me if my road goes far.", 'The Crimson Circle is broken. Master Klingenhand gave me his ring.',
        open_cond=[KANY('r_accept')], close_cond=[TDONE(f'{Q}_final', Q)])
st.task(f'{Q}_final', 'Seven Sigils', 'All seven duelists are dead. Bring their sigils to Master Klingenhand, outside the Golden Lance or wherever he has followed me.',
        'I gave Master Klingenhand all seven sigils.', parent=Q, open_cond=[TDONE(f'{Q}_{d[0]}', Q) for d in DUELISTS],
        close_cond=[KANY('t_sig7')], close_act=XP(200), target=MASTER)

# ================= 2. THE CODEX OF HIDDEN FIRE (Rakorium, Ferdok house) =================
QC, RK = 'arm_q_codex', 'loc02_rakorium'
BYE = '4d17e405-b426-4c21-83d2-a366d990b659'   # vanilla "Nothing, thank you."
WRAITH = 'arm_npc_rk_echo'
st.spawn_template(WRAITH, 'Echo of the Codex', 'npc_untoter_nekromant_loc08_gruft_boss', Faction='FaFeind', LEmax=450, LEmin=-10, AT=20, PA=16, MR=16,
                  AEmax=180, AE=180, IsVictoryWorthy=1, ZaKulminatio=18, ZaPlumbumbarum=16, ZaCorpofrigo=18, ZaSomnigravis=14, ZaHorriphobus=12,
                  SpecialAttackChances='MeleeAttack 3.0 0, Wuchtschlag 2.0 0, Klingensturm 2.0 0, Finte 2.0 0, Umreissen 1.0 0',   # vanilla typo '1.0.0' fixed
                  SetupStorage='Weapon/weapon_special_zauberstab/false/false;', SetupEquipment='', BasisXP=25, Stufe=15,
                  LootTable=st.loot_table('arm_lt_rk_echo', [('Money', 'Geld', 100, 5000, 1), ('Item', 'zutat_s_edelsteine', 100, 3, 1)]))
PAGE_REWARD = {  # page -> (action, Rakorium's reaction)
    'arm_q_page1': (GIVE('arm_scroll_haste', 2) + GIVE('arm_scroll_mend', 2),
                    "Of Embers! Ha! The first chapter! Look at this, look: the dragon's breath is a sentence, and the fire is only its punctuation. Here, take some scrolls. I wrote them myself. Mostly."),
    'arm_q_page2': (GIVE('arm_wand_frost'),
                    "Of Ashes! Burned, and yet the ink survived. That is not ink. Never mind what it is. Take this wand; I was using it to keep my tea cold. It is called the Wand of Rime."),
    'arm_q_page3': (GIVE('arm_j_rk_spectacles'),
                    "Of Bones! Moorbridge, of course, where else would bones keep secrets. You have earned my spare spectacles. Through them, magic looks like handwriting. Do not read your own."),
    'arm_q_page4': (GIVE('arm_scroll_trance', 2) + GOLD(50),
                    "Of Dreams! Grimmzahn's vaults! The orcs used it as a napkin, the barbarians. Some gold for your trouble, and two more scrolls. Now we only need to read it aloud..."),
}
rk_takes = [
    dict(id='arm_rk_r_codex', type='Response', kids=['arm_rk_t_offer'], cond=['!' + TA(RK, 'arm_rk_r_accept')], text='Master Rakorium, is there anything I could do for your research?'),
    dict(id='arm_rk_t_offer', type='Take', kids=['arm_rk_r_accept', 'arm_rk_r_later'],
         text="Research? Research! Yes! The Codex Pyrdaconis, the dream-book of the great dragon Pyrdacor himself, torn into four pages by a careless "
              "Hesindian novice and scattered to the winds. One went down the sewers right here in Ferdok, I am sure of it. The others? Wherever ruins, "
              "the dead and old stone walls keep things. You go everywhere, don't you? Bring them to me and I will prove, once and for all, that dragons "
              "dream. In verse!"),
    dict(id='arm_rk_r_accept', type='Response', kids=['arm_rk_t_accepted'], text='I will find your four pages, Master.'),
    dict(id='arm_rk_t_accepted', type='Take', kids=[BYE],
         text="Splendid! Sewers, ruins, crypts, vaults. All the nice places. Bring each page as you find it; every chapter makes the next one easier to read."),
    dict(id='arm_rk_r_later', type='Response', kids=['arm_rk_t_later'], text='Perhaps another time.'),
    dict(id='arm_rk_t_later', type='Take', kids=[BYE], text="Another time, another time. Everything is another time with you young people."),
]
for i, (pid, name, _, hint) in enumerate(PAGES, 1):
    act, line = PAGE_REWARD[pid]
    rk_takes += [dict(id=f'arm_rk_r_p{i}', type='Response', kids=[f'arm_rk_t_p{i}'], cond=[TA(RK, 'arm_rk_r_accept'), INV(pid), '!' + TDONE(f'{QC}_p{i}', QC)],
                      text=f'I found a page of your codex: "{name.split(": ")[1]}".'),
                 dict(id=f'arm_rk_t_p{i}', type='Take', kids=[BYE], act=TAKE(RK, pid, 1) + act, text=line)]
    st.task(f'{QC}_p{i}', name, f'Find the page {hint}.', f'I brought "{name}" to Rakorium.', parent=QC, state='unlocked',
            close_cond=[TA(RK, f'arm_rk_t_p{i}')], close_act=XP(25))
rk_takes += [
    dict(id='arm_rk_r_final', type='Response', kids=['arm_rk_t_final1'], cond=[TDONE(f'{QC}_p{i}', QC) for i in range(1, 5)] + ['!' + TDONE(f'{QC}_final', QC), 'IsTaskClosed task="respekt_drache" quest="loc08_gerling"; '],   # after Japhgur (audit A11)
         text='You have all four pages now, Master. What happens next?'),
    dict(id='arm_rk_t_final1', type='Take', kids=['arm_rk_r_final2'],
         text="Next? Next, we read it. Aloud. The proof only works aloud, it is a poem, you see. Ahem. 'In the dreaming of the Wyrm, the ink awakes, "
              "and what was written writes itself anew...' Hm. Is it warm in here? Is the page supposed to glow like that?"),
    dict(id='arm_rk_r_final2', type='Response', kids=['arm_rk_t_final2'], text='Master Rakorium, something is coming out of the pages!'),
    dict(id='arm_rk_t_final2', type='Take', act=GIVE('arm_m_rk_robe') + GIVE('arm_a_rk_best_hat') +
         f'CreateEntity category="NPC" templateId="{WRAITH}" how="spawnAtEntity" entity="{RK}" executeAfter="true" {A}',
         text="Oh. Oh dear. That is an Echo: the codex wrote its own reader. Proof that dragons dream! Proof that they have nightmares, too! "
              "Here, take my robe, the one I win arguments in, and my hat, my BEST hat, and hit it until it stops! I shall supervise from behind this chair!"),
]
st.extend_dialog(RK, {t: ['arm_rk_r_codex'] + [f'arm_rk_r_p{i}' for i in range(1, 5)] + ['arm_rk_r_final']
                      for t in ('FirstGreeting', 'Greeting_nach_03', 'Greeting_nach_05', 'Greeting_nach_08', 'dc44db63-a4d0-4275-b029-f7396fdb3a5b')}, rk_takes)
st.task(QC, 'The Codex of Hidden Fire', 'Master Rakorium wants the four lost pages of the Codex Pyrdaconis, the dream-book of the dragon Pyrdacor.',
        'Rakorium read the codex aloud. Dragons dream, and their dreams bite.', open_cond=[TA(RK, 'arm_rk_r_accept')], close_cond=[TDONE(f'{QC}_final', QC)])
st.task(f'{QC}_final', 'The Proof', 'All four pages are with Rakorium. He wants to read the codex aloud.', 'Rakorium read the codex. Something answered.',
        parent=QC, open_cond=[TDONE(f'{QC}_p{i}', QC) for i in range(1, 5)], close_cond=[TA(RK, 'arm_rk_t_final2')], close_act=XP(100), target=RK)

# ================= 3. WENDELIN RAUNEFUSS, TELLER OF RUMOURS (Wagoner's Home) =================
WEN, WD = 'arm_npc_wendelin', 'arm_dlg_wendelin'
st.npc(WEN, 'Wendelin Raunefuss, Teller of Rumours', 'loc02_fuhr_stadtbelebung_talk_08', 'location02_fuhrmannsheim',
       ('MarkerPoint', 'loc02_marker_sanfte_sau_entry'), (2.0, 0, 0), ScriptPreset='')
WH = ['r_fight', 'r_magic', 'r_country', 'r_rhulana', 'r_gwendala', 'r_forgrimm', 'r_treasure', 'r_bye']
st.dialog(WD, WEN, [
    dict(id='StartState', type='StartState', kids=['t_return', 't_first']),
    dict(id='t_first', type='Take', kids=WH,
         text="Psst. Over here. Wendelin Raunefuss, collector of rumours, whispers and half-truths. For you, the first ones are free. "
              "They are all free, actually. Nobody ever pays."),
    dict(id='t_return', type='Take', kids=WH, cond=[TA(WD, 't_first')], text="Back for more whispers? I have plenty."),
    dict(id='r_fight', type='Response', kids=['t_fight'], cond=[QDONE('loc04_mainquest')], text='Heard anything about skilled fighters?'),
    dict(id='t_fight', type='Take', kids=WH,
         text="Old Alrik Klingenhand drinks alone on the bench outside the Golden Lance. They say he trained the Crimson Circle: seven duelists who sell their swords. "
              "Ask him what happened to his son."),
    dict(id='r_magic', type='Response', kids=['t_magic'], text='Anything about magic?'),
    dict(id='t_magic', type='Take', kids=WH,
         text="Your house guest, Master Rakorium, mutters about torn pages of a dragon's codex. Ask him if there is anything you can do for his research. "
              "Mind you, one page went down the sewers, and nobody sane goes down there."),
    dict(id='r_country', type='Response', kids=['t_country'], text='And outside Ferdok?'),
    dict(id='t_country', type='Take', kids=WH,
         text="A trophy collector, Ulfried, trades on Praios Square by the bowyer, and follows the hunters wherever the game gets bigger. Pays in silver and jewellery for fangs and claws. "
              "And the chickens of Avestrue. Skin one. Trust me. Oh, and if you ever find a talking hat, do not listen to it."),
    dict(id='r_rhulana', type='Response', kids=['t_rhulana'], cond=[PARTY(RHULANA)], text='Anything my Amazon friend should hear?'),
    dict(id='t_rhulana', type='Take', kids=WH,
         text="An outcast Amazon, Sabeth Lionsbane, sells her sword to the Crimson Circle now. She carries a saber that belongs in Kurkum. If your road goes far enough, it will cross hers."),
    dict(id='r_gwendala', type='Response', kids=['t_gwendala'], cond=[PARTY(GWENDALA)], text='Anything about elves?'),
    dict(id='t_gwendala', type='Take', kids=WH,
         text="There is an elf who hunts elves for gold. Faelwen Duskarrow. He likes old trees and wet ground, and his bow sings."),
    dict(id='r_forgrimm', type='Response', kids=['t_forgrimm'], cond=[PARTY(FORGRIMM)], text='Anything about dwarves?'),
    dict(id='t_forgrimm', type='Take', kids=WH,
         text="A banished dwarf, Grimbart Ironbeard, guards something deep under the mountains. Dwarves do not say his name."),
    dict(id='r_treasure', type='Response', kids=['t_treasure'], text='Any treasure worth the trouble?'),
    dict(id='t_treasure', type='Take', kids=WH,
         text="Treasure? Dragons sleep on it, they say, and dwarves bury it so deep they forget where. Burned castles hide more than ash. "
              "And the dead keep diaries: read them. Where? If I knew, would I be standing in Wagoner's Home?"),
    dict(id='r_bye', type='Response', text='Thanks, Wendelin.'),
])

# ================= 4. Hooks into vanilla dialogs (balance audit N1, N2, N3) =================
# N3: the Blood Mountains woodcutter thanks you with his maul once his friend Holdwin is home (Forgrimm's chapter 2-3 two-hander)
WC = 'Loc03Holzfaeller01Dialog'
st.extend_dialog(WC, {'57e5f6dc-f297-490b-9334-15149a65b4fe': ['arm_wc_r_maul']}, [
    dict(id='arm_wc_r_maul', type='Response', kids=['arm_wc_t_maul'],
         cond=['IsQuestClosed quest="Loc03_Holzfaeller"; ', '!' + TA(WC, 'arm_wc_t_maul')], text='How is Holdwin doing?'),
    dict(id='arm_wc_t_maul', type='Take', act=GIVE('arm_r_splitting_maul') + XP(10),
         text="Up and grumbling, thanks to you. Here, take Holdwin's old maul. He says his back is done with it, and you look like you have "
              "more bandits ahead of you than he has logs. It splits both."),
])
# N1 dropped: Gwendala only joins after the ghost is defeated; her Elf wood lies on the tree-hollow skeleton instead (armory ELFWOOD_STOCK)
# N2: Pal'Na'Thar tempers the Fire weapon you chose. One response per weapon; only the one you carry shows.
PN = 'zyklop_panathar'
FIRE = [('weapon_unique_zyklopen_saebel', 'tp_firesong'), ('weapon_unique_zyklopen_schwert', 'tp_flamesong'), ('weapon_unique_zyklopen_axt', 'tp_firestrike'),
        ('weapon_unique_zyklopen_zweihandschwert', 'tp_flamestrike'), ('weapon_unique_zyklopen_zweihandaxt', 'tp_flamefury'),
        ('weapon_unique_zyklopen_speer', 'tp_firespike'), ('weapon_unique_zyklopen_schwererdolch', 'tp_firethorn'),
        ('weapon_unique_zyklopen_rapier', 'tp_sparksting'), ('weapon_unique_zyklopen_stab', 'tp_sparkstrike'),
        ('weapon_unique_zyklopen_bogen', 'tp_firestorm'), ('weapon_unique_zyklopen_armbrust', 'tp_flamesting')]
pn_takes = []
for wid, tp in FIRE:
    pn_takes += [dict(id=f'arm_pn_r_{tp}', type='Response', kids=[f'arm_pn_t_{tp}'],
                      cond=[f'IsInInventory category="Weapon" templateId="{wid}"; '] + ['!' + TA(PN, f'arm_pn_t_{t}') for _, t in FIRE],
                      text='Can you temper what I carry, master smith?'),
                 dict(id=f'arm_pn_t_{tp}', type='Take', act=f'CreateEntity category="Recipe" templateId="arm_rezept_{tp}" how="spawnInStorage" entity="Hero" number="1" executeAfter="true" {A}',
                      text="Temper it? Hrm. The Last Fire burns hot enough, but fire alone is not enough. Bring a scale of the Purplewyrm and good dwarven "
                           "steel, and follow these marks at any forge. The blade will remember this flame for a thousand years.")]
st.extend_dialog(PN, {'Last Greeting': [f'arm_pn_r_{tp}' for _, tp in FIRE]}, pn_takes)

# ================= 6. THE DUSKBORN PACK (Tallon, review 2 Nov) =================
# Ten black wolves, two lieutenants and Duskmane, the old pack-lord of the Rattelshof hills, on the road from Prancelot's goblin
# ambush up to the Linnorm cave (the one Tallon fight nobody skips). Duskmane carries his pelt and the plan for the Silverpelt
# Mantle (White Fur Mantle II). Offsets climb with the road (about 0.25 m up per metre east).
DUSK_AT = ('SpawnPoint', 'loc08_enc_parzalon_goblins', 'EncounterName')    # first point (338.9, 7.4, 128.6)
lt_dusk = st.loot_table('arm_lt_duskborn', [('Item', 'arm_tr_darkwolf_pelt', 40, 1, 1), ('Item', 'arm_tr_wolf_fang', 50, 1, 1)], picks=2)
lt_lieut = st.loot_table('arm_lt_dusk_lieutenant', [('Item', 'arm_tr_darkwolf_pelt', 100, 2, 1), ('Item', 'arm_tr_wolf_fang', 100, 2, 1)], picks=2)
lt_lord = st.loot_table('arm_lt_duskmane', [('Item', 'arm_rl_rattel_pelt', 100, 1, 1), ('Recipe', 'arm_rezept_wf_mantle2', 100, 1, 0),
                                            ('Item', 'arm_tr_darkwolf_pelt', 100, 2, 1), ('Item', 'arm_tr_wolf_fang', 100, 2, 1)], picks=4)
DUSKWOLF = dict(Faction='FaRaubtier', LEmin=-10, MR=6, **{k: 3 for k in ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')})
DUSK = [  # key, display, base, offset (east, up, north), stats
    ('duskmane', 'Duskmane, Lord of the Rattelshof Pack', 'Wolf_03', (24.0, 4.0, 8.0),
     dict(DUSKWOLF, LE=650, LEmax=650, PA=6, MR=14, BasisXP=60, Stufe=18, LootTable=lt_lord, FurriersLootTable='skin_wolf_groß',
          Immunity='overthrown;unconscious;stun;wound', RSKo=5, RSBr=5, RSRu=5, RSBa=5, AT=23, AW=6, ATW6=3, ATW6plus=5, Behaviour='clever_fighter', IsVictoryWorthy=1)),
    ('cinderjaw', 'Cinderjaw', 'Wolf_03', (21.0, 3.2, 11.0),
     dict(DUSKWOLF, LE=240, LEmax=240, AT=19, PA=4, MR=10, BasisXP=30, Stufe=16, LootTable=lt_lieut, FurriersLootTable='skin_wolf_groß',
          Immunity='overthrown;unconscious;stun;wound;burning;fire', RSBr=4, RSRu=4, ATW6=2, ATW6plus=5, AuraStatuseffect='burning', IsVictoryWorthy=1)),   # scorched muzzle: a fire aura
    ('gloomfang', 'Gloomfang', 'Wolf_03', (21.0, 3.2, 5.0),
     dict(DUSKWOLF, LE=240, LEmax=240, AT=19, PA=4, MR=10, BasisXP=30, Stufe=16, LootTable=lt_lieut, FurriersLootTable='skin_wolf_groß',
          Immunity='overthrown;unconscious;stun;wound', RSBr=4, RSRu=4, ATW6=2, ATW6plus=5, AW=10, IsVictoryWorthy=1)),   # fades into the shadows: hard to hit
] + [(f'duskborn_{i:02d}', 'Duskborn Wolf', 'Wolf_02', off,
      dict(DUSKWOLF, LE=75, LEmax=75, AT=17, PA=2, BasisXP=8, Stufe=13, LootTable=lt_dusk, FurriersLootTable='skin_wolf_mittel', ATW6plus=4))
     for i, off in enumerate([(17.0, 2.4, 6.0), (17.5, 2.5, 9.5), (18.5, 2.7, 12.5), (19.0, 2.8, 3.0), (20.0, 3.0, 8.0),
                              (22.5, 3.5, 13.0), (23.0, 3.6, 3.5), (25.5, 4.2, 11.0), (26.0, 4.3, 5.5), (27.5, 4.6, 8.5)], 1)]
DUSK_INFO = {'duskmane': 'Grey at the muzzle and black down the spine, the old lord of the Rattelshof pack. He has never once been in a hurry.',
             'cinderjaw': 'A black wolf with a scorched muzzle and eyes like coals. It fights at its lord\'s right hand.',
             'gloomfang': 'A lean black wolf that seems to fade into the shadows between the trees. It fights at its lord\'s left hand.'}
for key, disp, base, off, over in DUSK:
    st.monster(f'arm_mo_{key}', disp, base, 'location08', DUSK_AT, off, info=DUSK_INFO.get(key, 'A black wolf of the Rattelshof hills, big and quiet.'), **over)

# ================= 5. THE MAD PACK (Dark Forest, review 1 Nov) =================
# Alvina's wolves have gone moon-mad: 13 wolves, the alpha Greymaw and the white storm-wolf Stormhowl (lightning aura of the forest's
# nature-spirit bears), placed together in the western woods of location03. Hard for chapter 2 on purpose. Their pelts, sinew, mane
# and heartstone exist nowhere else. They are Alwene's wolves (their vanilla templates carry her name): Greymaw wears a witch's
# charm, and Knowall, the witches' talking toad, takes it and passes on the witches' notes, the Moonhowl plans (player, 2 Nov:
# no more goatherd). Greymaw's fang also belongs in Ulfried's Grand Collection (build_quest_avestrue.py).
QM, KD = 'arm_q_madpack', 'Loc03AllwissDialog'
KNOWALL_HUBS = ['b0b12ac0-c29e-4970-a2bb-94f0111e485c', '01e7ba34-9c92-4002-84f7-35f7c5812ed9']   # "You are friend of Knowall" / "Why did you come to Knowall?"
PACK_AT = ('SpawnPoint', 'loc03_enc_random_26', 'EncounterName')   # first spawn point of a wild-woods encounter; offsets follow its other points
MPELT, MSINEW = 'arm_tr_moonmad_pelt', 'arm_tr_moon_sinew'
lt_pack = st.loot_table('arm_lt_madwolf', [('Item', MPELT, 70, 1, 1), ('Item', MSINEW, 50, 1, 1), ('Item', 'arm_tr_wolf_fang', 50, 1, 1)], picks=3)
qitem('arm_q_wolf_charm', 'robable_glueksbringer', "Witch's Wolf-Charm", "Owl feathers and red thread, braided into the alpha's fur. The witches "
      "of the Dark Forest tie these on the wolves they keep. Knowall, their talking toad, will know what it means.", quest=QM)
lt_alpha = st.loot_table('arm_lt_greymaw', [('Item', 'arm_q_wolf_charm', 100, 1, 1), ('Item', 'arm_tr_greymaw_fang', 100, 1, 1), ('Item', 'arm_tr_greymaw_mane', 100, 1, 1), ('Item', MPELT, 100, 2, 1), ('Item', MSINEW, 100, 3, 1),
                                            ('Item', 'arm_tr_wolf_fang', 100, 2, 1)])   # every entry drops
lt_storm = st.loot_table('arm_lt_stormhowl', [('Item', 'arm_tr_storm_heart', 100, 1, 1), ('Item', MPELT, 100, 1, 1), ('Item', MSINEW, 100, 1, 1)], picks=3)
WOLF = dict(Faction='FaRaubtier', LEmin=-10, PA=0, MR=4, **{k: 3 for k in ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')})
PACK = [  # key, display, base, offset, stats
    ('greymaw', 'Greymaw, the Mad Alpha', 'Wolf_03_loc03_alwene', (0.0, 0, 0.0),
     dict(WOLF, LE=320, LEmax=320, PA=4, MR=6, BasisXP=20, Stufe=13, LootTable=lt_alpha, FurriersLootTable='skin_wolf_groß',
          Immunity='overthrown;unconscious;stun;wound', RSKo=4, RSBr=4, RSRu=4, RSBa=4, AT=20, ATW6=2, ATW6plus=5, AW=7, Behaviour='clever_fighter', IsVictoryWorthy=1)),
    ('stormhowl', 'Stormhowl', 'wolf_weiss_loc00z6', (-5.3, 0, 3.6),
     dict(WOLF, LE=150, LEmax=150, AT=18, PA=2, MR=14, BasisXP=18, Stufe=12, LootTable=lt_storm, AuraStatuseffect='blitzDichFind', ATW6=2, ATW6plus=4, IsVictoryWorthy=1,
          Immunity='poison;overthrown;unconscious;stun;wound')),
] + [(f'madwolf_{i:02d}', 'Moon-mad Wolf' if i <= 9 else 'Moon-mad Hunter', 'Wolf_02_loc03_alwene' if i <= 9 else 'Wolf_03_loc03_alwene', off,
      dict(WOLF, LE=40 if i <= 9 else 55, LEmax=40 if i <= 9 else 55, AT=14 if i <= 9 else 16, BasisXP=4 if i <= 9 else 6, Stufe=8 if i <= 9 else 10,
           LootTable=lt_pack))
     for i, off in enumerate([(1.5, 0, 1.5), (-1.5, 0, -1.5), (1.5, 0, -1.5), (-1.5, 0, 1.5), (-7.0, 0, 5.0), (-4.0, 0, 5.2), (-6.8, 0, 2.2),
                              (5.3, 0.5, 0.0), (3.0, 0.4, -3.0), (5.5, 0.6, -2.8), (-2.5, 0, 3.5), (0.0, 0, -3.0), (2.8, 0.2, 1.2)], 1)]
INFO = {'greymaw': 'The alpha of the mad pack. Grey as iron, and it does not flinch from fire.',
        'stormhowl': 'A white wolf whose fur crackles like a coming storm. Lightning answers when it is struck.'}
for key, disp, base, off, over in PACK:
    st.monster(f'arm_mo_{key}', disp, base, 'location03', PACK_AT, (off[0], off[1] + 1.5, off[2]), info=INFO.get(key, 'A wolf with silver in its eyes. It does not run.'), **over)

PLAN = lambda rid: f'CreateEntity category="Recipe" templateId="{rid}" how="spawnInStorage" entity="Hero" number="1" executeAfter="true" {A}'
PACK_DEAD = ['IsDead who="arm_mo_greymaw"; ', 'IsDead who="arm_mo_stormhowl"; ']
KN = lambda take: f'TalkedAbout dialogId="{KD}" takeId="{take}"; '
st.extend_dialog(KD, {h: ['arm_mp_r_charm', 'arm_mp_r_early'] for h in KNOWALL_HUBS}, [
    dict(id='arm_mp_r_early', type='Response', kids=['arm_mp_t_early'], cond=['IsDead who="arm_mo_greymaw"; ', '!IsDead who="arm_mo_stormhowl"; ', '!' + KN('arm_mp_t_charm')],
         text='I took this charm from a mad wolf.'),
    dict(id='arm_mp_t_early', type='Take',
         text="Croak! Mother's charm, from the grey one. But Knowall still hears the white one, crackle crackle, in the west. Storm in its fur. "
              "Bring Knowall the charm when both are quiet. Croak."),
    dict(id='arm_mp_r_charm', type='Response', kids=['arm_mp_t_charm'], cond=PACK_DEAD + [HAS('arm_q_wolf_charm', 1), '!' + KN('arm_mp_t_charm')],
         text='I found this charm in the fur of a mad wolf. The pack is dead.'),
    dict(id='arm_mp_t_charm', type='Take',
         act=TAKE('Loc03_Allwiss', 'arm_q_wolf_charm', 1) + ''.join(PLAN(f'arm_rezept_{k}') for k in ('mh_mantle', 'mh_jerkin', 'mh_breeches', 'mh_grips', 'mh_bow', 'tl_wolf2')) + XP(60),
         text="Croak... Mother Alwene's charm. Storm came down on the western woods and the wolves went bad, bad, eyes like coals. Knowall could not "
              "help. You helped. Mother left skins-and-sinew notes with Knowall for whoever ends it. Moon-mad pelt makes leather no blade bites, "
              "sinew makes a string that sings. Take, take. Knowall is thankful, croak, croak."),
])
st.task(QM, 'The Mad Pack', "The witches of the Dark Forest keep wolves, and something has driven them mad: they hunt as one pack in the western "
        "woods, led by the grey alpha Greymaw and the white wolf Stormhowl. The grey one wore a witch's charm. Knowall, the witches' talking toad, "
        "will know what it means.", "The mad pack is dead. Knowall gave me the witches' notes on moon-mad pelt and sinew.",
        open_cond=['IsDead who="arm_mo_greymaw"; '], close_cond=[TDONE(f'{QM}_return', QM)])   # opens with the alpha's death
st.task(f'{QM}_hunt', 'Greymaw and Stormhowl', 'Kill the two leaders of the mad pack in the western woods. The rest of the pack will not stand aside.',
        'Greymaw and Stormhowl are dead.', parent=QM, state='unlocked', close_cond=PACK_DEAD, close_act=XP(40), target='arm_mo_greymaw')
st.task(f'{QM}_return', "The Witch's Charm", "Bring the witch's charm to Knowall, the witches' talking toad.", 'I gave Knowall the charm.', parent=QM,
        open_cond=[TDONE(f'{QM}_hunt', QM)], close_cond=[KN('arm_mp_t_charm')], close_act=XP(40), target='Loc03_Allwiss')

# 7. the Thieves' Guild lives in its own file (shares this namespace)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret_guild.py'), encoding='utf-8').read())

m.write(out)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('\n'.join(ICONS) + '\n')
sc.close(); shutil.rmtree(snap, ignore_errors=True)
for _l in getattr(m, 'ground_log', []): print('  ground:', _l)
print('ok static', len(m.static), 'game', len(m.game), 'texts', len(m.locale))
