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

# Fury (player, 2 Nov: "go crazy with damage on unique monsters, make each one the final boss of its area"): on top of the
# life above, every unique outside the tutorial gets half again its life, one more damage die and +3 damage, +2 attack, +2 parry
# if it parries at all, and uses its own special moves three times as often. Tutorial bosses (level 1-3 party) only hit +1 harder.
TUTORIAL = {'loc01_wolf_weissfell', 'Baer_Loc01', 'Wolfsratte_loc01_boss'}
FURY_LIFE, FURY_DICE, FURY_PLUS, FURY_AT, FURY_PA, FURY_MOVES = 1.5, 1, 3, 2, 2, 3.0

def _moves(spec):
    """Special-attack weights x FURY_MOVES (plain melee stays): 'BearSweepAttack 1.0 0' -> 'BearSweepAttack 3.0 0'."""
    out = []
    for part in [p.strip() for p in (spec or '').split(',') if p.strip()]:
        bits = part.split()
        if len(bits) == 3 and bits[0] != 'MeleeAttack':
            try: bits[1] = f'{float(bits[1]) * FURY_MOVES:.1f}'
            except ValueError: pass
        out.append(' '.join(bits))
    return ', '.join(out)

def toughened(row, entry):
    """New column values for a template row (dict) under a TOUGH entry."""
    le, rs, mr, at, imm = entry
    tut = row.get('Id') in TUTORIAL
    le = max(le, row['LEmax'] or 0) if tut else int(max(le, row['LEmax'] or 0) * FURY_LIFE)
    new = {'LEmax': le, 'LE': le, 'MR': max(mr, row['MR'] or 0), 'AT': (row['AT'] or 0) + at + (0 if tut else FURY_AT)}
    if 'ATW6plus' in row: new['ATW6plus'] = (row['ATW6plus'] or 0) + (1 if tut else FURY_PLUS)
    if 'IsVictoryWorthy' in row: new['IsVictoryWorthy'] = 1   # every unique ends with the victory pose (player, 2 Nov)
    if not tut:
        if 'ATW6' in row: new['ATW6'] = (row['ATW6'] or 1) + FURY_DICE
        if (row.get('PA') or 0) > 0: new['PA'] = row['PA'] + FURY_PA
        if row.get('SpecialAttackChances'): new['SpecialAttackChances'] = _moves(row['SpecialAttackChances'])
    for z in ZONES:
        if z in row and (row[z] or 0) > 0: new[z] = row[z] + rs
    if imm:
        new['Immunity'] = ';'.join(dict.fromkeys([x for x in (row.get('Immunity') or '').split(';') if x] + imm.split(';')))
    return {k: v for k, v in new.items() if k in row and v != row[k]}

# the pack's own legends and the mad-pack leaders get the same treatment in their builders (build_quest_avestrue, build_secret_quests)
OWN_WOUND_IMMUNE = True
