# ================= 7. THE THIEVES' GUILD (player, 2 Nov; docs/THIEVES_GUILD_PLAN.md) =================
# Exec'd by build_secret_quests.py (shares its namespace: m, st, qitem, stats, FENCE, SABER, HEAVY, TA, QDONE, HAS, GIVE, GOLD, TAKE, XP, A).
# Four jobs from Cano, one after each chapter. The prize is carried by the gang's boss: pick his pocket (he can be robbed, the prize
# is his stolen-goods table) or call him out and fight the gang for it. Each finished job brings a new guild member into the lower
# hall with their own shop (Velane also trains). Cano's own stock is never touched: his two vanilla versions share the hall and
# giving items "to Cano" by name could hit the hidden one.
from armory_data import GUILD_STOCK, GUILD_REWARD
CD, CBYE = 'Cuano', 'a00bb64e-1d1b-4da3-b744-d3d2076ce211'   # Cano's dialog and his vanilla "I have no wishes and am happy" answer
HALL = 'dungeon02_diebesgilde'
QG = 'arm_q_guild'
JOBS = [  # n, gate quest, prize (id, base, name, desc), level, anchor, gang [(key, name, clone, weapon, stats, attacks, boss?)], pitch, done text, gold
    (1, 'Loc03_Main', ('arm_q_tg_strongbox', 'loc04_schmuckschatulle', "The Dark Eyes' Strongbox", 'A heavy iron strongbox with the Dark Eye sign on the lid. Cano wants it unopened.'),
     'location02_hafen', ('MarkerPoint', 'loc02_hafen_sa_deal_goto_01'),
     [('ulgar', 'Ulgar Crowsfoot, Dark Eye Lieutenant', 'loc02_schwarzauge_schlafend_1', 'Langdolch', stats(190, 18, 15, 3, 6, (14, 12, 13, 11, 15, 15, 14, 13), 20, 10), FENCE, True)] +
     [('dehexer', 'Dark Eye Hedge-Witch', 'loc02_trainer_praios_magie', 'Magierrapier', dict(stats(120, 15, 12, 2, 8, (13, 14, 13, 12, 13, 13, 12, 11), 9, 8), **HEXER), FENCE, False)] +
     [(f'darkeye{i}', 'Dark Eye Cutthroat', 'loc02_schwarzauge_schlafend_2', 'Saebel', stats(110, 16, 12, 2, 4, (13, 10, 12, 9, 13, 14, 13, 13), 8, 7), SABER, False) for i in (1, 2, 3)],
     "There is a job, if you are as good as the rumours say. What is left of the Dark Eyes meets at the harbour, at their old deal spot, "
     "and their lieutenant Ulgar Crowsfoot carries the gang's last strongbox wherever he goes. I want it. Lift it from his belt, quietly, "
     "or take it from his cold hands; Phex does not mind which, only the Dark Eyes will.",
     "Ulgar's strongbox! Unopened, too. You have a future here. Silas! Come down, we have a new friend. He is our fence: tell him I sent you.", 60),
    (2, 'Burg_Grimmzahn', ('arm_q_tg_silver', 'loc04_grabschmuck', "The Baron's Silver", "Silver plate from Castle Grimmzahn's treasury, wrapped in a soldier's cloak."),
     'location03', ('MarkerPoint', 'loc03_marker_cut_hinterhalt_group_banditen01'),   # the Silver Falls close for good after Grimmzahn
     [('brackwald', 'Sergeant Brackwald, Deserter', 'loc02_trainer_praios_nahkampf', 'Langschwert', stats(280, 20, 17, 5, 7, (15, 11, 12, 11, 13, 14, 16, 17), 26, 13), HEAVY, True)] +
     [('dshexer', 'Renegade Battle-Mage', 'loc02_trainer_praios_magie', 'Magierrapier', dict(stats(170, 17, 14, 3, 10, (14, 15, 13, 12, 14, 14, 13, 12), 11, 11), **HEXER), FENCE, False)] +
     [(f'deserter{i}', 'Grimmzahn Deserter', 'loc02_trainer_praios_nahkampf', 'Speer' if i == 2 else 'Langschwert',
       stats(160, 17, 14, 4, 5, (14, 10, 11, 10, 12, 13, 15, 15), 10, 10), HEAVY, False) for i in (1, 2, 3, 4)],
     "While the orcs were busy with Grimmzahn, a few of its own soldiers emptied the treasury and ran. Their sergeant, Brackwald, camps on "
     "the old road through the Blood Mountains with the Baron's silver, waiting for the roads to clear. The silver should travel. With us. He keeps it on him, of course.",
     "The Baron's silver. The Baron will never miss what he believes the orcs took. Ravik! Our new star needs clothes that do not rattle.", 90),
    (3, 'loc08_gerling', ('arm_q_tg_ledger', 'loc02_lieferschein', "The Silent Hand's Ledger", 'Names, debts and bribes of the Silent Hand of Tallon, in a careful cipher.'),
     'location08', ('MarkerPoint', 'Mapmarker_loc08_Hesperia_Schutt'),
     [('kessar', 'Master Kessar of the Silent Hand', 'loc02_milde_gabe_dieb_2', 'Langdolch', dict(stats(340, 22, 18, 4, 9, (15, 14, 15, 12, 17, 17, 14, 13), 32, 15), AW=10), FENCE, True)] +
     [('shhexer', 'Silent Hand Hexer', 'loc02_trainer_praios_magie', 'Magierrapier', dict(stats(200, 18, 15, 3, 12, (14, 16, 14, 12, 15, 15, 13, 12), 13, 13), **HEXER), FENCE, False)] +
     [(f'silent{i}', 'Silent Hand Knife', 'loc02_milde_gabe_dieb_1' if i % 2 else 'loc02_mr_pickpocket', 'Langdolch',
       dict(stats(190, 19, 15, 3, 7, (14, 12, 13, 11, 15, 16, 13, 13), 12, 12), AW=8), FENCE, False) for i in (1, 2, 3, 4)],
     "Tallon has its own guild. The Silent Hand. They have been selling our people to the town watch for years, and their master Kessar keeps "
     "the ledger that proves it. He meets his knives in the rubble outside the walls. Bring me that ledger and their whole house of cards falls.",
     "Kessar's ledger! Half of Tallon's watch is in here. And look who came with you: Velane, his own blade master. She says she was tired "
     "of the company. She teaches now. Down there.", 120),
    (4, 'Loc09_Aldessia', ('arm_q_tg_crystal', 'loc09_thesiskristall', "Aldessia's Portal Crystal", "A crystal that hums when you hold it near a doorway. Aldessia's best-kept secret."),
     'location09', ('MarkerPoint', 'loc09_marker_aldessia_house'),
     [('morwena', "Morwena, Aldessia's Apprentice", 'loc02_trainer_praios_magie', 'Magierrapier',
       dict(stats(380, 20, 16, 4, 14, (15, 17, 15, 13, 15, 15, 14, 12), 36, 17), AEmax=200, AE=200, ZaIgnifaxius=16, ZaPlumbumbarum=14, ZaHorriphobus=12, ZaSomnigravis=12, ZaArmatrutz=12,
            ZaFulminictus=14), FENCE, True)] +
     [('apprentice1', 'Black Apprentice', 'loc02_trainer_praios_magie', 'Magierrapier',
       dict(stats(220, 18, 14, 3, 12, (14, 15, 14, 12, 14, 14, 13, 12), 14, 14), AEmax=100, AE=100, ZaIgnifaxius=12, ZaFulminictus=10), FENCE, False)] +
     [(f'hireling{i}', 'Hired Axe of Murolosh', 'Loc09_Drachentoeter_02', 'Langschwert', stats(300, 21, 17, 6, 8, (15, 10, 11, 9, 12, 12, 17, 18), 14, 15), HEAVY, False)
      for i in (1, 2)],
     "Aldessia is gone and her apprentices are picking her house clean before the dwarves think of it. The best piece in there is a crystal that "
     "opens her portals; her favourite, Morwena, wears it on a chain. Imagine what a guild can do with a door to anywhere. I can imagine it very well.",
     "A door to anywhere, and it fits in my pocket. Wendrik! Wake up, old fox, you have a customer. Our forger. He never touched anything in his life.", 150),
]
MEMBERS = {  # job -> (key, name, clone, offset from the lower-hall entry, greeting, teaches)
    1: ('silke', 'Silas Quickfingers, Guild Fence', 'loc02_milde_gabe_dieb_1', (-2.5, 0, 2.0),
        "Cano says you are one of us now. Good. I buy what you should not have and sell what nobody saw leave. Blades, stars, boots that keep quiet.", ''),
    2: ('ravik', 'Ravik Blackstitch, Guild Tailor', 'loc02_mr_pickpocket', (2.5, 0, 2.0),
        "Iryan leather, the black kind. Cut close, oiled silent, no buckle to catch the moon. Buy the plans and the leather, and any workbench will do.", ''),
    3: ('velane', 'Velane the Shade, Blade Master', 'loc02_amazone_typ2', (-2.5, 0, -3.5),
        "Kessar paid me to teach his knives. You paid me by taking his ledger. So I teach you instead. It is a better use of my time.",
        'TaDolche;TaFechtwaffen;TaWurfwaffen;TaSchleichen;TaTaschendiebstahl;TaSchloesser;TaFallenEntschaerfen;SF_Finte;SF_GezielterStich;SF_Todesstoss;'
        'SF_Klingensturm;SF_GezielterWurf;SF_Kraftwurf;SF_Meisterwurf;SF_Meisterparade;SF_Klingenwand;SF_Windmuehle;SF_Ausweichen1;SF_Ausweichen2;SF_Ausweichen3;'),
    4: ('wendrik', 'Old Fox Wendrik, Forger', 'Loc09_Drachentoeter_02', (2.5, 0, -3.5),
        "Wendrik. Forger, jeweller, honest dwarf. Mostly honest. Everything on this table was made by hand, and none of it by mine.", ''),
}
_hubs = list(dict.fromkeys(r[0] for r in m.s.execute(
    "select t.TakeId from _Story_DialogTakes t join _Story_DialogTakeChildMapping c on c.TakeGUID=t.TakeGUID where t.DialogId=? and c.TakeChildId=?", (CD, CBYE))))
assert _hubs, 'Cano has no hub with the goodbye answer'
WHERE = {1: 'Ulgar Crowsfoot, lieutenant of the Dark Eyes, carries it at their old deal spot in Ferdok harbour.',
         2: 'Sergeant Brackwald, a deserter, keeps it on him on the old road through the Blood Mountains.',
         3: 'Master Kessar of the Silent Hand keeps it on him in the rubble outside Tallon.',
         4: "Morwena, Aldessia's favourite apprentice, wears it while her gang empties Aldessia's house in Murolosh."}
for n, gate, (pid, pbase, pname, pdesc), lvl, anchor, gang, pitch, done, gold in JOBS:
    qitem(pid, pbase, pname, pdesc, quest=QG, robable=1)
    rob = st.loot_table(f'arm_lt_tg_rob{n}', [('Item', pid, 100, 1, 1)])
    ids = []
    for i, (gk, gname, gclone, gweap, gsts, gatt, boss) in enumerate(gang):
        gid = f'arm_npc_tg_{gk}'; ids.append(gid)
        ang = 2 * math.pi * i / len(gang); off = (0.0, 0, 0.0) if boss else (2.5 * math.cos(ang), 0, 2.5 * math.sin(ang))
        extra = dict(CanRob=1, StolenGoodsTable=rob, IsVictoryWorthy=1) if boss else {}
        lt = st.loot_table(f'arm_lt_tg_{gk}', [('Money', 'Geld', 100, (gold if boss else 8) * 100, 1), ('Item', 'zutat_s_edelsteine', 60 if boss else 20, 2 if boss else 1, 1)])
        st.npc(gid, gname, gclone, lvl, anchor, (off[0], off[1] + 1.0, off[2]), park=True, SpecialAttackChances=moves(gweap), LootTable=lt, **gsts, **extra)   # full moves; 1 m up
        st.stock(gid, 'Weapon', gweap, lootable=1)
        if boss: st.stock(gid, 'Item', pid, lootable=1)
    boss = ids[0]
    draw = ''.join(f'SetFaction faction="FaFeind" who="{g}" executeAfter="true" {A}EquipBestCloseRangeWeapon who="{g}" executeAfter="true" {A}' for g in ids)
    draw += ''.join(ARMATRUTZ(g) for g in ids)
    st.dialog(f'arm_dlg_tg_{gang[0][0]}', boss, [
        dict(id='StartState', type='StartState', kids=['t_hello']),
        dict(id='t_hello', type='Take', kids=['r_fight', 'r_bye'], text="Lost? This corner is taken. Walk on, and keep your hands where my friends can see them."),
        dict(id='r_fight', type='Response', kids=['t_fight'], text="Cano sends his regards. Hand it over."),
        dict(id='t_fight', type='Take', act=draw, text="Cano? Then he can have it back in pieces. Yours."),
        dict(id='r_bye', type='Response', text='Just passing through.'),
    ])
    prev = [TA(CD, f'arm_tg_t_done{n - 1}')] if n > 1 else []
    m_key, m_name, m_clone, m_off, m_hello, m_teach = MEMBERS[n]
    mid = f'arm_npc_tg_{m_key}'
    st.npc(mid, m_name, m_clone, HALL, ('Entry', 'loc02_entry_diebesgilde_runkel'), m_off, merchant=True, park=True, ScriptPreset='',
           **({'TeachableSkills': m_teach} if m_teach else {}))
    for typ, key in GUILD_STOCK[m_key]:
        iid = f'arm_rezept_{key}' if typ == 'Recipe' else (f'arm_{key}' if key.startswith('tg_') else key)
        st.stock(mid, typ, iid, n=25 if key.endswith('stars') else 1)
    st.dialog(f'arm_dlg_tg_{m_key}', mid, [
        dict(id='StartState', type='StartState', kids=['t_hello']),
        dict(id='t_hello', type='Take', kids=['r_trade'] + (['r_train'] if m_teach else []) + ['r_bye'], text=m_hello),
        dict(id='r_trade', type='Response', act=f'ShowTradeUI trader="{mid}" executeAfter="true" {A}', text='Show me what you have.'),
        dict(id='r_train', type='Response', act=f'ShowTrainerUI trainer="{mid}" disciple="SelectionLeader" executeAfter="true" {A}', text='Teach me.'),
        dict(id='r_bye', type='Response', text='Later.')])
    takes = [
        dict(id=f'arm_tg_r_job{n}', type='Response', kids=[f'arm_tg_t_job{n}'], cond=[QDONE(gate)] + prev + ['!' + TA(CD, f'arm_tg_r_accept{n}')],
             text='Any work for someone with quiet hands?' if n == 1 else 'Do you have another job for me, Cano?'),
        dict(id=f'arm_tg_t_job{n}', type='Take', kids=[f'arm_tg_r_accept{n}', CBYE], text=pitch),
        dict(id=f'arm_tg_r_accept{n}', type='Response', kids=[f'arm_tg_t_accept{n}'], text='Consider it done.'),
        dict(id=f'arm_tg_t_accept{n}', type='Take', kids=[CBYE], act=''.join(st.arrive(g) for g in ids),
             text="Good. Quiet is better, but I will take loud. Bring it here, and nobody else needs to know."),
        dict(id=f'arm_tg_r_hand{n}', type='Response', kids=[f'arm_tg_t_done{n}'],
             cond=[TA(CD, f'arm_tg_r_accept{n}'), HAS(pid, 1), '!' + TA(CD, f'arm_tg_t_done{n}')], text=f'Here it is: {pname}.'),
        dict(id=f'arm_tg_t_done{n}', type='Take', kids=[CBYE], text=done,
             act=TAKE(CD, pid, 1) + GOLD(gold) + GIVE(f'arm_{GUILD_REWARD[n]}') + XP(60 + 30 * n) + st.arrive(mid)),
    ]
    st.extend_dialog(CD, {h: [f'arm_tg_r_job{n}', f'arm_tg_r_hand{n}'] for h in _hubs}, takes, position=30 + 2 * n)
    st.task(f'{QG}_{n}', pname, f'Cano wants {pname}. {WHERE[n]} Steal it from them unseen, or take it by force, and bring it to Cano.',
            f'Cano has {pname}.', parent=QG, state='unlocked', open_cond=[TA(CD, f'arm_tg_r_accept{n}')], close_cond=[TA(CD, f'arm_tg_t_done{n}')], target=boss)
st.task(QG, "Phex's Due", "Cano has work for me now that I have made a name for myself. The Guild of Thieves pays well, and it grows with every job I do.",
        'I have done four jobs for Cano. The whole guild knows my name.', open_cond=[TA(CD, 'arm_tg_r_accept1')], close_cond=[TA(CD, 'arm_tg_t_done4')])
