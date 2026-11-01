"""Unique beasts and bosses: toughness by story weight (review 1 Nov). Used by build_remastered.py (applies it to the game's own
monsters) and build_hard_ending.py (scales on top of these values instead of the vanilla ones, so the two stack).

Why: late-game wound and critical weapons one-shot most unique monsters, because almost none resist wounds (only the Evil Tree
did). Every unique gets wound immunity, more magic resistance (willpower), a little armour (like an Armatrutz) and a life pool that
matches its place in the story. Mother Ratzinsky is the reference: 500 life in vanilla, but 3 armour, no wound resistance.

Each entry: template type, id -> (life, armour bonus on every protected zone, magic resistance, attack bonus, extra immunities).
"""
W = 'wound'
TOUGH = {
    # tutorial (Avestrue): bosses for a level 1-3 party
    ('Monster', 'loc01_wolf_weissfell'):              (90, 1, 6, 1, W),          # White Fur
    ('Monster', 'Baer_Loc01'):                        (120, 1, 6, 0, W),         # the cave bear
    ('Monster', 'Wolfsratte_loc01_boss'):             (60, 1, 2, 1, W),          # the mill's giant wolf rat
    # chapter 1, Ferdok
    ('Monster', 'Wolfsratte_loc02_mutter_ratzinski'): (520, 2, 10, 2, W),        # Mother Ratzinsky
    ('Monster', 'Gruftassel_gross_loc02_sanfte_sau_schabe'): (340, 1, 6, 0, W),  # the Gentle Sow's cockroach
    ('Monster', 'Smaragdspinne_loc02'):               (260, 1, 14, 0, W),        # the oracle spider
    ('Monster', 'Riesenkrabbe_loc02'):                (260, 1, 6, 0, W),         # the Marascan crab
    # chapter 2-3
    ('Monster', 'boeser_baum'):                       (380, 2, 8, 0, ''),        # the Evil Tree (already wound-immune)
    ('Monster', 'Untotes_Maultier'):                  (220, 2, 8, 1, W),         # the undead mule
    ('Monster', 'Smaragdspinne_loc05'):               (340, 1, 15, 1, W),        # the vault spider of Grimmzahn
    # Tallon
    ('MonsterLarge', 'Tatzelwurm_v2'):                (850, 2, 10, 1, W),        # the Linnorm
    ('NPC', 'Oger_04_kraeftig_loc08_boss'):           (650, 2, 6, 0, W),         # the Ogre Chief
    ('MonsterLarge', 'Japhgur'):                      (1500, 2, 15, 1, W),       # the Purple Wyrm
    # Murolosh and later
    ('NPC', 'Steingolem_loc09_aldessia'):             (350, 1, 10, 0, W),        # the stone golem
    ('Monster', 'gruftassel_boss_loc09'):             (220, 1, 15, 0, W),        # the large crypt lice
    ('NPC', 'Zyklopenskelett_loc10'):                 (875, 2, 10, 0, W),        # the cyclops skeleton
    ('Monster', 'Smaragdspinne_loc11'):               (420, 1, 16, 1, W),        # the crystal-cave spiders
    ('NPC', 'Arombolosch_Wahnsinn'):                  (313, 1, 12, 0, W),
    ('NPC', 'Aldessia_feindlich'):                    (160, 1, 14, 0, W),
}
ZONES = ('RSKo', 'RSBr', 'RSRu', 'RSBa', 'RSLA', 'RSRA', 'RSLB', 'RSRB')

def toughened(row, entry):
    """New column values for a template row (dict) under a TOUGH entry."""
    le, rs, mr, at, imm = entry
    new = {'LEmax': max(le, row['LEmax'] or 0), 'LE': max(le, row['LEmax'] or 0), 'MR': max(mr, row['MR'] or 0), 'AT': (row['AT'] or 0) + at}
    for z in ZONES:
        if z in row and (row[z] or 0) > 0: new[z] = row[z] + rs
    if imm:
        new['Immunity'] = ';'.join(dict.fromkeys([x for x in (row.get('Immunity') or '').split(';') if x] + imm.split(';')))
    return {k: v for k, v in new.items() if k in row and v != row[k]}

# the pack's own legends and the mad-pack leaders get the same treatment in their builders (build_quest_avestrue, build_secret_quests)
OWN_WOUND_IMMUNE = True
