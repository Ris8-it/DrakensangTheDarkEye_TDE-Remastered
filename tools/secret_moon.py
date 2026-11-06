# ================= 8. THE MOON-THREAD (review 6 Nov, part 2) =================
# Exec'd by build_secret_quests.py after the Mad Pack (shares its namespace: m, st, qitem, stats, moves, TA, TDONE, HAS, GIVE, GOLD,
# TAKE, XP, PLAN, KD, KN, KNOWALL_HUBS, A, sc, make_icon, ROOT, out, ICONS).
# The player's idea: the Mad Pack's reward (the Moonhowl plans) is only useful after Tallon, so a long questline now runs from the
# Dark Forest to Tallon and pays out there. Story (player-approved mix of "the thread of the moon" and "the collector"):
#   1. Dark Forest  Knowall finds a silver thread in Alwene's charm: not witch-work. He knots it (quest item) and sends you to the
#                   potion-folk of Ferdok.
#   2. Grimtooth    (optional, one-way region) a trapper's camp on the road to the castle: broken cages, three mad wolves, a torn bill
#                   of sale: "the Collector pays for every beast that bites itself".
#   3. Ferdok       Auralia: moon-silver, spun from moonlight. Only the little folk can do that; show it to one who answers straight.
#   4. Tallon       the leprechaun (after his riddle; also the one who later takes over Auralia's stall): he spun it, and sold it to
#                   Baltram Seyfried, a collector who wants to put the moon on a leash, Ulfried's old rival. Baltram is binding the
#                   mother of the moon-mad wolves at the witches' dancing place. The leprechaun wants his moonlight back and opens
#                   a moon road (vanilla LoadLocation, like Aydan's move to the Golden Lance).
#   5. The dancing place: five chained wolves, one by each skull pillar (storm, ember, frost, rot, shadow); each one killed puts its
#      pillar out. Baltram and two trappers. When all are down, the Moon-Mother rises from the fire: three phases, and she cannot
#      die (LEmin, as vanilla's last boss). Beaten, she yields; the leprechaun appears with the choice:
#        cut the thread and let her go  -> Moon-Mother's Tear (amulet), the plans; Knowall and the witches are glad
#        take her pelt                  -> the Moonmother Mantle, the plans; Knowall is quiet about it
#      Then he offers the way back: to Tallon (next to his meadow), down into the forest, or stay.
# Untested in game: the moon road (LoadLocation from our dialog), parked monsters walking in, SwitchState on the skull pillars,
# HealthCritical phases, SetLEmin on a monster, the Tanzplatz party entry after the vanilla story used it.
QT = 'arm_q_moon'
TQ = lambda t: TDONE(f'{QT}_{t}', QT)
TANZ, LVL = ('MarkerPoint', 'Loc03_Marker_Tanzplatz'), 'location03'          # (211.4, 43.0, -166.7), the plateau is ~30 m across
ARRIVE_AT = 'loc03_entry_cut_hexentanzplatz_party01'                         # vanilla party entry on the plateau (213.0, 43.0, -162.9)
BACK_TALLON, BACK_FOREST = 'loc03_entry_cut_kobold_party', 'loc03_entry_party_hexen_nach_tanzplatz'   # 3 m from his meadow / vanilla's way down
MOM = 'arm_mo_mt_mother'
KNOT = 'arm_q_moon_knot'
LEP = [('loc08_kobold_dialog', '66427107-65da-4325-9346-9ad5899b7a33'),     # Tallon, after his riddle: "You're back again. Another game?"
       ('d_loc02_kobold_auralia', '2a3ad568-8147-4dcd-af0f-1b766c3b705c')]  # Ferdok, once he has taken over Auralia's stall
AUR, AUR_HUB = 'd_loc02_auralia', 'SecondGreeting'                           # Auralia before she joins (Count's Town)
LSAID = lambda take: [[TA(d, take) for d, _ in LEP]]                         # said in either of his dialogs (an Or group)
LNOT = lambda take: ['!' + TA(d, take) for d, _ in LEP]
MSG = lambda who, key, text: (m.text(key, text), f'ShowOverHeadMessage msg="{key}" who="{who}" {A}')[1]
SHAKE = lambda who: f'PlayShakeEffect target="{who}" range="60" intensity="0.6" duration="1.5" {A}'

# ---------------- rewards ----------------
D = lambda d: int(d * 100)
def moon_icon(key, brush, tier):
    custom = os.path.join(ROOT, 'assets', 'remastered_icons', f'arm_{key}.dds'); dst = os.path.join(out, 'icons', f'arm_{key}.dds')
    if os.path.isfile(custom): shutil.copy2(custom, dst)
    elif not os.path.isfile(dst): make_icon(os.path.join(ROOT, 'tools', 'research', 'out', 'icons_vanilla', brush.split('/')[-1] + '.dds'), dst, tier)
    if f'arm_{key}.dds' not in ICONS: ICONS.append(f'arm_{key}.dds')
    return f'icons/arm_{key}'
from dsa import mods_text, insert as _insert
TEAR_MODS = 'MR +2 LEmax +8 AUmax +8 IN +1 TaWildnisleben +2'
_pe = m.status('PeArmMoontear', "Moon-Mother's Tear", mods_text(TEAR_MODS), start=TEAR_MODS)
m.template('Jewelry', 'amulett_ch', 'arm_mt_tear', "Moon-Mother's Tear", "A drop of moonlight that never dried, given freely by the mother of the "
           "moon-mad wolves when you cut her thread. On quiet nights it hums like a wolf far away.\\n\\n" + mods_text(TEAR_MODS).replace(', ', '\\n'),
           PermanentEffect=_pe, Value=D(40), IconBrush=moon_icon('mt_tear', 'icons/magic_amulett_01', 'legendary'))
# the Moonmother Mantle: the Moonhowl Mantle (armory_v2) lined with the Moon-Mother's own pelt; one armour point more on chest and back
_mh = dict(sc.execute("select * from _Template_Armor where Id='arm_mh_mantle'").fetchone())
MANTLE_MODS = 'TaSchleichen +3 MR +2 AT +1 KK +1 AUmax +10'
_pe2 = m.status('PeArmMoonmantle', 'Moonmother Mantle', mods_text(MANTLE_MODS), start=MANTLE_MODS)
_mh.update(Id='arm_mt_mantle', Name='arm_mt_mantle', LookAtText='lookat_arm_mt_mantle', InfoIdentified='infoid_arm_mt_mantle', PermanentEffect=_pe2,
           Value=D(40), RSBr=(_mh['RSBr'] or 0) + 1, RSRu=(_mh['RSRu'] or 0) + 1)
for _k in ('LookAtUnidentified', 'InfoUnIdentified'):
    if _k in _mh: _mh[_k] = 'lookat_arm_mt_mantle' if _k.startswith('Look') else 'infoid_arm_mt_mantle'
assert sum((_mh[k] or 0) for k in ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')) <= 10, 'late leather shoulders cap (DESIGN_RULES 4)'
m.static += ['-- Armor arm_mt_mantle', _insert('_Template_Armor', _mh)]; m.undo_static.append("DELETE FROM _Template_Armor WHERE Id='arm_mt_mantle';")
m.text('lookat_arm_mt_mantle', 'Moonmother Mantle')
m.text('infoid_arm_mt_mantle', "The Moonhowl Mantle, lined with the pelt of the Moon-Mother herself. Silver in the dark, heavy as a promise. "
       "Wolves go quiet when you pass.\\n\\n" + mods_text(MANTLE_MODS).replace(', ', '\\n'))
m.templates.append(('Armor', 'arm_mt_mantle', _mh))
MH_PLANS = ''.join(PLAN(f'arm_rezept_{k}') for k in ('mh_mantle', 'mh_jerkin', 'mh_breeches', 'mh_grips', 'mh_bow', 'tl_wolf2'))

# ---------------- quest items ----------------
qitem('arm_q_moon_bill', 'loc02_lieferschein', 'Torn Bill of Sale', "Half a page, chewed at the edge: \"...cages to be delivered to the "
      "dancing place before the moon is full. The Collector pays in gold for every beast that bites itself, double for the mother. "
      "Moon-thread as agreed. B.S.\"", quest=QT)

# ---------------- 2. Grimtooth: the trappers' camp on the road to the castle (optional; the region closes for good) ----------------
CAMP_AT = ('MarkerPoint', 'marker_loc05_toter_mann_1')     # (110.2, 14.6, 227.3); the camp is on clear ground 45 m below it
CAMP = (-26.0, -3.9, -37.0)                                 # -> (84.2, 10.7, 190.3), 20 m from any quest object (.work/inspect/spot2.py)
lt_cage = st.loot_table('arm_lt_mt_cagebreaker', [('Item', 'arm_q_moon_bill', 100, 1, 1), ('Item', MPELT, 100, 1, 1), ('Item', MSINEW, 100, 1, 1),
                                                   ('Money', 'Geld', 100, 600, 1)])
for key, disp, base, off, over in (
        ('cagebreaker', 'Cage-Breaker', 'Wolf_03_loc03_alwene', (0.0, 0, 0.0),
         dict(WOLF, LE=170, LEmax=170, AT=17, PA=3, MR=8, BasisXP=12, Stufe=11, LootTable=lt_cage, FurriersLootTable='skin_wolf_groß', ATW6=2, ATW6plus=4,
              Immunity='overthrown;unconscious;stun;wound', IsVictoryWorthy=1)),
        ('cagewolf_1', 'Moon-mad Wolf', 'Wolf_02_loc03_alwene', (2.0, 0, 1.5), dict(WOLF, LE=60, LEmax=60, AT=15, BasisXP=5, Stufe=9, LootTable=lt_pack)),
        ('cagewolf_2', 'Moon-mad Wolf', 'Wolf_02_loc03_alwene', (-2.0, 0, 1.5), dict(WOLF, LE=60, LEmax=60, AT=15, BasisXP=5, Stufe=9, LootTable=lt_pack))):
    st.monster(f'arm_mo_mt_{key}', disp, base, 'location05', CAMP_AT, (CAMP[0] + off[0], CAMP[1] + off[1] + 1.0, CAMP[2] + off[2]),
               info='A wolf with silver in its eyes and a broken iron collar round its neck.' if key != 'cagebreaker' else
               'The biggest of the escaped wolves. A snapped chain still hangs from its collar.', **over)

# ---------------- 4. the cast of the dancing place (parked until the moon road opens) ----------------
CHAINED = [  # key, display, base, offset from the plateau marker (toward its skull pillar), skull pillar, stats, info
    ('storm', 'Storm-Chained', 'wolf_weiss_loc00z6', (3.0, 0, 11.7), 'loc03_schaedelhalter_01',
     dict(AuraStatuseffect='blitzDichFind', Immunity='poison;overthrown;unconscious;stun;wound', MR=14), 'Its white fur crackles. Lightning answers when it is struck.'),
    ('ember', 'Ember-Chained', 'Wolf_03', (12.0, 0, 7.7), 'loc03_schaedelhalter_02',
     dict(AuraStatuseffect='burning', Immunity='overthrown;unconscious;stun;wound;burning;fire'), 'Its muzzle smoulders and its eyes are coals.'),
    ('frost', 'Frost-Chained', 'wolf_weiss_loc00z6', (11.6, 0, -7.3), 'loc03_schaedelhalter_03',
     dict(AuraStatuseffect='eiseskaelte', Immunity='overthrown;unconscious;stun;wound'), 'Rime grows on the stones where it stands.'),
    ('rot', 'Rot-Chained', 'Wolf_03', (-5.9, 0, 8.7), 'loc03_schaedelhalter_04',
     dict(AuraStatuseffect='rotten_stench', Immunity='poison;smell;overthrown;unconscious;stun;wound'), 'It stinks of the grave, and so does the air around it.'),
    ('shadow', 'Shadow-Chained', 'Wolf_03', (-10.4, 0, 0.5), 'loc03_schaedelhalter_05',
     dict(AW=12, Immunity='overthrown;unconscious;stun;wound'), 'A lean black wolf that is hard to look at. Blows slide off the dark around it.'),
]
CHAIN_BASE = dict(WOLF, Faction='FaAllFriendly', LE=180, LEmax=180, AT=18, PA=4, MR=10, BasisXP=25, Stufe=15, ATW6=2, ATW6plus=5,
                  FurriersLootTable='skin_wolf_groß', IsVictoryWorthy=1, RSKo=4, RSBr=4, RSRu=4, RSBa=4)   # chained: friendly until Baltram looses them
lt_chain = st.loot_table('arm_lt_mt_chained', [('Item', MPELT, 100, 1, 1), ('Item', MSINEW, 100, 1, 1), ('Item', 'arm_tr_wolf_fang', 100, 1, 1)])
for key, disp, base, off, pillar, over, info in CHAINED:
    st.monster(f'arm_mo_mt_{key}', disp, base, LVL, TANZ, (off[0], off[1] + 1.0, off[2]), info=info, park=True, **{**CHAIN_BASE, 'LootTable': lt_chain, **over})
lt_mom = st.loot_table('arm_lt_mt_mother', [('Item', MPELT, 100, 3, 1), ('Item', MSINEW, 100, 3, 1), ('Item', 'arm_tr_wolf_fang', 100, 3, 1)])
st.monster(MOM, 'The Moon-Mother', 'wolf_weiss_loc00z6', LVL, TANZ, (0.5, 1.0, -5.0), park=True,
           info='The mother of the moon-mad wolves. Silver from muzzle to tail, and a thread of light runs from her collar into the fire.',
           **dict(WOLF, LE=900, LEmax=900, LEmin=5, AT=21, PA=5, AW=8, MR=16, BasisXP=90, Stufe=19, LootTable=lt_mom, FurriersLootTable='skin_wolf_groß',
                  ATW6=3, ATW6plus=6, RSKo=5, RSBr=5, RSRu=5, RSBa=5, AuraStatuseffect='eiseskaelte', Behaviour='clever_fighter', IsVictoryWorthy=1,
                  Immunity='poison;overthrown;unconscious;stun;wound'))   # LEmin 5: she cannot die; she yields (vanilla's last boss does the same)
lt_baltram = st.loot_table('arm_lt_mt_baltram', [('Money', 'Geld', 100, 3000, 1), ('Item', 'zutat_s_edelsteine', 100, 2, 1)])
lt_trapper = st.loot_table('arm_lt_mt_trapper', [('Money', 'Geld', 100, 500, 1), ('Item', MPELT, 50, 1, 1)])
st.npc('arm_npc_mt_baltram', 'Baltram Seyfried, the Collector', 'loc02_haendler_graf_waffen', LVL, TANZ, (-1.4, 1.0, -10.3), park=True, turn=180,
       SpecialAttackChances=moves('Jagdspiess'), LootTable=lt_baltram, IsVictoryWorthy=1, **stats(280, 20, 15, 5, 12, (15, 14, 14, 13, 13, 15, 15, 16), 40, 16))
st.stock('arm_npc_mt_baltram', 'Weapon', 'Jagdspiess', lootable=1)
for i, off in ((1, (-5.4, 1.0, -8.3)), (2, (4.6, 1.0, -10.3))):
    st.npc(f'arm_npc_mt_trapper{i}', "Baltram's Trapper", 'loc08_haendler_dieb', LVL, TANZ, off, park=True, turn=180,
           SpecialAttackChances=moves('Haumesser'), LootTable=lt_trapper, **stats(150, 17, 13, 4, 6, (14, 11, 12, 10, 14, 15, 14, 15), 15, 12))
    st.stock(f'arm_npc_mt_trapper{i}', 'Weapon', 'Haumesser', lootable=1)
st.npc('arm_npc_mt_kobold', 'The Leprechaun', 'loc08_kobold', LVL, TANZ, (-2.4, 1.0, 3.7), park=True, ScriptPreset='')
CAST = ['arm_npc_mt_baltram', 'arm_npc_mt_trapper1', 'arm_npc_mt_trapper2'] + [f'arm_mo_mt_{c[0]}' for c in CHAINED]
FOES_DEAD = [f'IsDead who="{w}"; ' for w in CAST]
PT = {k: st.point(f'arm_mt_rim_{k}', LVL, TANZ, off) for k, off in (('n', (1.0, 1.0, 9.0)), ('e', (9.0, 1.0, 0.0)), ('s', (-1.0, 1.0, -9.0)), ('w', (-9.0, 1.0, -1.0)))}
CALL = lambda tpl, at: ''.join(f'CreateEntity category="Monster" templateId="{tpl}" how="spawnAtEntity" entity="{PT[k]}" number="1" executeAfter="true" {A}' for k in at)

# ---------------- dialogs ----------------
# 3. Auralia (before she joins; her stall in the Count's Town)
st.extend_dialog(AUR, {AUR_HUB: ['arm_mt_r_aur']}, [
    dict(id='arm_mt_r_aur', type='Response', kids=['arm_mt_t_aur'], cond=[HAS(KNOT, 1), '!' + TA(AUR, 'arm_mt_t_aur')] + LNOT('arm_mt_t_lep'),
         text="Knowall the toad gave me this knot. The thread in it is not witch-work. Do you know what it is?"),
    dict(id='arm_mt_t_aur', type='Take', kids=['arm_mt_r_aur2'], act=GIVE('crafted_a_heiltrank', 2) + XP(40),
         text="A toad gave you... never mind, old Auralia has heard stranger. Let me see. Oh. Oh my. Cold as a well and it doesn't tarnish. "
              "That is moon-silver, child: moonlight spun on a spindle. No smith can make that, and no alchemist either, I've tried for "
              "forty years. Only the little folk can spin the moon. If you ever meet one of them who answers you straight, which they never "
              "do, show him this knot and watch his face."),
    dict(id='arm_mt_r_aur2', type='Response', kids=['arm_mt_t_aur2'], text='The little folk?'),
    dict(id='arm_mt_t_aur2', type='Take', text="Leprechauns, goblins' cleverer cousins, the ones who turn honest men into chickens for a laugh. "
         "Funny thing: my own great recipe has a riddle in it that wants one of them, too. Here, two of my potions for the trouble. "
         "Moonlight in a wolf's charm... someone wanted those wolves very badly."),
])

# 4. the leprechaun (Tallon after his riddle, or Ferdok at Auralia's stall)
GO = (''.join(st.arrive(w) for w in CAST) + st.arrive('arm_npc_mt_kobold') + ''.join(f'SwitchState entity="{c[4]}" state="Active" {A}' for c in CHAINED)
      + f'LoadLocation location="{LVL}" entry="{ARRIVE_AT}" executeAfter="true" {A}')
for did, hub in LEP:
    st.extend_dialog(did, {hub: ['arm_mt_r_lep', 'arm_mt_r_road', 'arm_mt_r_road2']}, [
        dict(id='arm_mt_r_lep', type='Response', kids=['arm_mt_t_lep'], cond=[HAS(KNOT, 1)] + LNOT('arm_mt_t_lep'),
             text='Have you ever seen a thread like this?'),
        dict(id='arm_mt_t_lep', type='Take', kids=['arm_mt_r_lep2'], act=XP(50),
             text="Heeheehee, seen it? I SPUN it! Moonlight, three nights' worth, on my best spindle. Where did you... oh. Oh no. In a wolf's "
                  "charm? He said he wanted it for a necklace! A grim fellow with a ledger and a smile like a trap. Baltram something. "
                  "Seyfried! He paid in gold, and I like gold, and now look."),
        dict(id='arm_mt_r_lep2', type='Response', kids=['arm_mt_t_lep2'], text='What does he want with moonlight?'),
        dict(id='arm_mt_t_lep2', type='Take', kids=['arm_mt_r_lep3'],
             text="To put the moon on a leash, of course! Tie moon-thread into a wolf's charm and the wolf goes moon-mad. Tie enough wolves and "
                  "their mother comes looking for them, and then you tie HER. The mother of the moon-mad wolves, the last one there is. What a "
                  "pelt, for a man who collects pelts. He'll be doing it where the witches dance, up among the old skulls in your Dark Forest. "
                  "The thread wants to go back there, I can feel it."),
        dict(id='arm_mt_r_lep3', type='Response', kids=['arm_mt_t_lep3'], text='Then I have to get there.'),
        dict(id='arm_mt_t_lep3', type='Take', kids=['arm_mt_r_road', 'arm_mt_r_later'],
             text="Walk? It's half a kingdom away, you'd arrive with a beard. No, no. I want my moonlight back, and you want the collector, so: "
                  "I'll open the moon road. One step and you're there. Say when. I'll come along and watch, heeheehee, from a safe distance."),
        dict(id='arm_mt_r_road', type='Response', kids=['arm_mt_t_road'], cond=LSAID('arm_mt_t_lep') + ['!' + TQ('road')] + LNOT('arm_mt_t_road'),
             text='Open the moon road. We are ready.'),
        dict(id='arm_mt_t_road', type='Take', act=GO,
             text="Hold hands, or don't, it makes no difference, I just like it when people do. Lirum, larum, moon on a drum... and away!"),
        # a second trip (left before it was over): only the road, the cast is already there
        dict(id='arm_mt_r_road2', type='Response', kids=['arm_mt_t_road2'], cond=[[TA(d, 'arm_mt_t_road') for d, _ in LEP]] + ['!' + TQ('choice')],
             text='Open the moon road again.'),
        dict(id='arm_mt_t_road2', type='Take', act=f'LoadLocation location="{LVL}" entry="{ARRIVE_AT}" executeAfter="true" {A}',
             text="Back up among the skulls? Brave, or forgetful. Lirum, larum!"),
        dict(id='arm_mt_r_later', type='Response', text='Not yet. We need to prepare.'),
    ])

# 5. Baltram at the fire
LOOSE = ''.join(f'SetFaction faction="FaFeind" who="{w}" executeAfter="true" {A}EquipBestCloseRangeWeapon who="{w}" executeAfter="true" {A}'
                for w in CAST[:3]) + ''.join(f'SetFaction faction="FaRaubtier" who="arm_mo_mt_{c[0]}" executeAfter="true" {A}' for c in CHAINED)
st.dialog('arm_dlg_mt_baltram', 'arm_npc_mt_baltram', [
    dict(id='StartState', type='StartState', kids=['t_hello']),
    dict(id='t_hello', type='Take', kids=['r_who', 'r_stop'],
         text="Visitors, at this hour? Mind the skulls, they're older than your family. Baltram Seyfried, collector. You've heard of my rival, I expect: "
              "Ulfried Pelzfeld, who buys teeth from children. I don't buy. I catch."),
    dict(id='r_who', type='Response', kids=['t_plan'], text="You tied moon-thread into the witches' charms. You drove those wolves mad."),
    dict(id='t_plan', type='Take', kids=['r_stop'],
         text="Mad is such an ugly word. Devoted. Each of these five carries a little of the moon, and the moon carries their mother. When the five "
              "skulls burn together she'll come out of that fire to find her children, and she'll find a collar instead. The last Moon-Mother "
              "in Aventuria, on my wall. Ulfried will weep."),
    dict(id='r_stop', type='Response', kids=['t_fight'], text='It ends here, Baltram.'),
    dict(id='t_fight', type='Take', act=LOOSE + SHAKE('arm_npc_mt_baltram'),
         text="Does it? Lads, off with the chains. Let's see how devoted they are."),
])
# the leprechaun on the plateau: the choice, then the way back
FREE = (f'PlayVisualEffect effect="transversalis_an" target="{MOM}" fixedposition="false" {A}'
        f'TransferEntity entity="{MOM}" location="_graveyard_" entryPoint="hellgate" track="0" {A}' + GIVE('arm_mt_tear') + MH_PLANS + XP(80))
PELT = (f'SetLEmin le="-10" entity="{MOM}" {A}Hurt who="{MOM}" fixedDamage="999" dice="6" diceAmount="1" showNoDamage="false" damageType="physical" {A}'
        + GIVE('arm_mt_mantle') + MH_PLANS + XP(60))
BACK = [dict(id='r_tallon', type='Response', kids=['t_go_tallon'], text='Take us back to Tallon.'),
        dict(id='t_go_tallon', type='Take', act=f'LoadLocation location="location08" entry="{BACK_TALLON}" executeAfter="true" {A}',
             text="Back to my meadow, then, and mind the cats. Lirum, larum!"),
        dict(id='r_forest', type='Response', kids=['t_go_forest'], text='Down into the forest.'),
        dict(id='t_go_forest', type='Take', act=f'TransferEntity group="PlayerParty" location="{LVL}" entryPoint="{BACK_FOREST}" executeAfter="true" {A}',
             text="Down the hill with you. The toad will want to hear all about it. Toads always do."),
        dict(id='r_stay', type='Response', text="We'll stay a while.")]
DONE = [TA('arm_dlg_mt_kobold', 't_free'), TA('arm_dlg_mt_kobold', 't_pelt')]
st.dialog('arm_dlg_mt_kobold', 'arm_npc_mt_kobold', [
    dict(id='StartState', type='StartState', kids=['t_after', 't_choice', 't_wait']),
    dict(id='t_wait', type='Take', kids=['r_stay'], text="Psst! Don't mind me. I'm not here. Heeheehee. Go on, go on, I'm watching from behind this skull."),
    dict(id='t_choice', type='Take', kids=['r_free', 'r_pelt'], cond=[TQ('mother')],
         text="Stop, stop! She's beaten. Look at her: the thread's still in her, see, running into the fire. My moonlight. Now then. Snip the "
              "thread and she runs home, and the madness runs out of her pack with her. Or... she has the finest pelt in all the world, and "
              "nobody would ever know. I don't mind which. Well. I do, a little."),
    dict(id='r_free', type='Response', kids=['t_free'], text='Cut the thread. Let her go.'),
    dict(id='t_free', type='Take', kids=[r['id'] for r in BACK if r['type'] == 'Response'], act=FREE,
         text="Snip! Heeheehee, look at her go! Over the skulls and gone. There, my moonlight is mine again, and here's a drop of it for you: she "
              "left it on the stones, and she meant it. And these: the witches' notes on moon-mad pelt and sinew. Your collector had them in his "
              "satchel, he stole those too. Now. Home?"),
    dict(id='r_pelt', type='Response', kids=['t_pelt'], text='Her pelt is mine.'),
    dict(id='t_pelt', type='Take', kids=[r['id'] for r in BACK if r['type'] == 'Response'], act=PELT,
         text="Oh. Well. Quick, at least, you were quick. The thread is loose now; I'll take my moonlight off her. Here, a mantle-maker's "
              "dream, and the witches' notes your collector stole, they were in his satchel. You should know how to work it. Now. Home?"),
    dict(id='t_after', type='Take', kids=[r['id'] for r in BACK if r['type'] == 'Response'], cond=[DONE],
         text="Still here? The skulls are getting ideas. Where to?"),
] + BACK)

# Knowall's epilogue
st.extend_dialog(KD, {h: ['arm_mt_r_kn_free', 'arm_mt_r_kn_pelt'] for h in KNOWALL_HUBS}, [
    dict(id='arm_mt_r_kn_free', type='Response', kids=['arm_mt_t_kn_free'], cond=[TA('arm_dlg_mt_kobold', 't_free'), '!' + KN('arm_mt_t_kn_free')],
         text='The thread is cut. The Moon-Mother ran free.'),
    dict(id='arm_mt_t_kn_free', type='Take', act=XP(30),
         text="Croak! Knowall heard her! Singing, over the hills, all night. Mother Alwene cried, the good kind. You are friend of the witches now, "
              "truly, truly. Croak."),
    dict(id='arm_mt_r_kn_pelt', type='Response', kids=['arm_mt_t_kn_pelt'], cond=[TA('arm_dlg_mt_kobold', 't_pelt'), '!' + KN('arm_mt_t_kn_pelt')],
         text='The collector is dead. So is the Moon-Mother.'),
    dict(id='arm_mt_t_kn_pelt', type='Take', act=XP(10),
         text="Croak... Hunters hunt. Knowall knows. The madness is gone from the woods, that is good. But the woods are quiet now. So quiet."),
])

# ---------------- journal ----------------
st.task(QT, 'The Moon-Thread', "Knowall found a thread of cold silver in the witch's wolf-charm and swears it is not witch-work. Someone tied it into "
        "the charm, and then the wolves went mad. He knotted it for me: it twitches when madness is near.",
        "The thread is back where it came from. The Moon-Mother's story is over, and Baltram Seyfried's collection is one beast short.",
        open_cond=[KN('arm_mp_t_charm')], close_cond=[TQ('choice')])
st.task(f'{QT}_silver', 'Not Witch-Work', "Knowall says the potion-folk of Ferdok buy moon-things. An alchemist might know what this thread is.",
        "Auralia knew: moon-silver, spun from moonlight. Only the little folk can spin it.", parent=QT, state='unlocked',
        close_cond=[[TA(AUR, 'arm_mt_t_aur')] + LSAID('arm_mt_t_lep')[0]], close_act=XP(20))
st.task(f'{QT}_cages', 'Empty Cages', "The knot twitches. Somewhere near here something mad is loose.",
        "Escaped wolves at an abandoned trappers' camp, and a torn bill of sale: someone called the Collector pays for every beast that bites itself.",
        parent=QT, open_cond=['IsInLocation who="Hero" location="location05"; ', KN('arm_mp_t_charm')],
        close_cond=[[HAS('arm_q_moon_bill', 1)] + LSAID('arm_mt_t_lep')[0]], close_act=XP(40), target='arm_mo_mt_cagebreaker')
st.task(f'{QT}_little', 'One Who Answers Straight', "Show the knot to one of the little folk, if I ever meet one who answers straight.",
        "The leprechaun spun the thread himself, and sold it to Baltram Seyfried.", parent=QT, open_cond=[TA(AUR, 'arm_mt_t_aur')],
        close_cond=LSAID('arm_mt_t_lep'))
st.task(f'{QT}_road', 'The Moon Road', "Baltram Seyfried, a collector of pelts, means to bind the mother of the moon-mad wolves at the witches' dancing "
        "place in the Dark Forest. The leprechaun will open the moon road whenever I am ready.",
        "The moon road took us to the witches' dancing place.", parent=QT, open_cond=LSAID('arm_mt_t_lep'),
        close_cond=['IsInLocation who="Hero" location="location03"; ', [TA(d, 'arm_mt_t_road') for d, _ in LEP]])
st.task(f'{QT}_baltram', 'The Collector', "Baltram waits by the witches' fire with his trappers and five chained wolves, one by each skull.",
        "Baltram Seyfried's collecting days are over.", parent=QT, open_cond=[TQ('road')], close_cond=FOES_DEAD[:1], close_act=XP(80), target='arm_npc_mt_baltram')
for key, disp, base, off, pillar, over, info in CHAINED:
    st.task(f'{QT}_skull_{key}', f'The {disp.split("-")[0]} Skull', f"The {disp.lower()} wolf is bound to a skull on its pillar.",
            f"The {disp.lower()} wolf is dead, and its skull went dark.", parent=QT, open_cond=[TQ('road')],
            close_cond=[f'IsDead who="arm_mo_mt_{key}"; '], close_act=f'SwitchState entity="{pillar}" state="Inactive" {A}')
RISE = (st.arrive(MOM) + SHAKE(MOM) + MSG(MOM, 'arm_mt_msg_rise', 'The last skull goes dark. Something howls inside the fire.'))
st.task(f'{QT}_mother', 'The Moon-Mother', "The five skulls are dark, and the mother of the moon-mad wolves has come out of the fire.",
        "The Moon-Mother is beaten. She lies by the fire and does not get up.", parent=QT, open_cond=FOES_DEAD, open_act=RISE,
        close_cond=['IsInLocation who="Hero" location="location03"; ', f'HealthCritical who="{MOM}" percent="0.03"; '],
        close_act=(f'SetFaction faction="FaAllFriendly" who="{MOM}" executeAfter="true" {A}'
                   + MSG('arm_npc_mt_kobold', 'arm_mt_msg_kobold', 'Psst! Over here! Stop hitting her!')), target=MOM)
_HURT = lambda pct: ['IsInLocation who="Hero" location="location03"; ', TQ('baltram'), f'HealthCritical who="{MOM}" percent="{pct}"; ']
st.task(f'{QT}_howl', 'Moonhowl', 'She throws back her head and howls at a moon nobody else can see.', 'Two wolves answered her howl out of the dark.',
        parent=QT, open_cond=FOES_DEAD, close_cond=_HURT('0.75'), close_act=SHAKE(MOM) + CALL('Wolf_03_loc03_alwene', ('n', 's')))
st.task(f'{QT}_dark', 'The Moon Goes Dark', 'The fire dims. She is hard to see now.', 'The moon went dark, and she moved like a shadow.',
        parent=QT, open_cond=FOES_DEAD, close_cond=_HURT('0.5'), close_act=SHAKE(MOM) + f'SetStatusEffect who="{MOM}" id="ArmQuickstep" {A}' + CALL('Wolf_03', ('e', 'w')))
st.task(f'{QT}_chain', 'The Last Chain', 'The thread from her collar burns white.', 'She tore at the last chain and fought like the moon itself was angry.',
        parent=QT, open_cond=FOES_DEAD, close_cond=_HURT('0.25'), close_act=SHAKE(MOM) + f'SetStatusEffect who="{MOM}" id="ArmTrance" {A}')
st.task(f'{QT}_choice', 'Thread or Pelt', "The leprechaun is waiting by the fire. The thread is still in her.",
        "I made my choice by the witches' fire.", parent=QT, open_cond=[TQ('mother')], close_cond=[DONE], close_act=XP(50), target='arm_npc_mt_kobold')
# the leprechaun steps out once she is beaten (he has been on the plateau all along, behind a skull)
