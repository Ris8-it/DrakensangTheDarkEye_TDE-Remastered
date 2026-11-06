"""World Systems (optional module): the engine layers turned into play, built with tools/layers.py.

  * Wayside shrines of five gods (Ferdok, Dark Forest, Moorbridge, Tallon, Murolosh): use one for a 15-minute party blessing.
    layers 10 (usable object), 2 (can: gate: one blessing at a time), 9 (timed status on every party member), 7 (hint trigger)
  * Regrowing herb patches in five wilderness areas (Dark Forest, Moorbridge, Silver Falls, Tallon, Gruldur): they grow back every third time you enter the area.
    layers 11 (herb + entry point), 6 (level-enter script with a counter)
  * Hunting grounds in the Dark Forest and around Tallon: wolves, boars and bears return every 20 minutes (4 times),
    from the second visit on. layers 12 (encounter on proven spawn spots), 6 (armed by the level-enter script)
  * Elite fighters rally when badly hurt; wounded beasts go into a frenzy. layer 1 (on:DamageTaken presets, vanilla presets kept)
  * Wolves howl to call the pack before they attack (the game's own unused wolf behaviour, revived). layer 3
  * Ogres get a ground slam that can knock the party down. layer 5 (scripted attack through their own move list)

Usage: python -I tools/build_world_systems.py "<game>/export/db/armory_backup" mods/world_systems
Static parts (presets, slam, wolf behaviour for spawned wolves) reach existing saves; placed content (shrines, herbs,
hunting grounds, level scripts, placed wolves/ogres) needs a new game or tools/maint/sync_save_world.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod
from layers import write_sync_bat, Layers, A, C, Not, And, Or, PARTY

db, out = sys.argv[1], sys.argv[2]
m = Mod(db, 'worldsys')
L = Layers(m)
NS = 'lay'
report = []

# ============================================================== shrines
SHRINES = [  # key, god, level, anchor, offset, modifiers, effect text, stage
    ('Phex', 'Phex', 'location02_praios', ('WorkBench', 'AlchemyWorkBench'), (2.5, 0, 1.5), 'TaFeilschen +2 TaSchloesser +1 TaTaschendiebstahl +1',
     'Haggle +2, Pick Locks +1, Pick Pocket +1', 'early'),
    ('Firun', 'Firun', 'location03', ('WorkBench', 'BowCraftingWorkBench'), (2.5, 0, 1.5), 'TaWildnisleben +2 TaTierkunde +2 TaBogen +1',
     'Survival +2, Animal Lore +2, Bow +1', 'mid'),
    ('Peraine', 'Peraine', 'location04', ('WorkBench', 'AlchemyWorkBench'), (2.5, 0, 1.5), 'TaHeilkundeWunden +2 TaHeilkundeGift +2 TaPflanzenkunde +2',
     'Treat Wounds +2, Treat Poisons +2, Plant Lore +2', 'mid'),
    ('Rondra', 'Rondra', 'location08', ('WorkBench', 'ForgingWorkBench'), (2.5, 0, 1.5), 'AT +1 PA +1 MU +1',
     'Attack +1, Parry +1, Courage +1', 'late'),
    ('Ingerimm', 'Ingerimm', 'location09', ('WorkBench', 'ForgingWorkBench'), (2.5, 0, 1.5), 'KK +1 KO +1 TaSchmieden +2',
     'Strength +1, Constitution +1, Blacksmith +2', 'endgame'),
]
LORE = {'Phex': 'A coin-polished fox of grey stone. Merchants and thieves alike leave a copper here before a deal.',
        'Firun': 'A weathered stone with a bear\'s paw carved into it. Hunters touch it before they go out.',
        'Peraine': 'A stone basin of rainwater with dried herbs laid along its rim.',
        'Rondra': 'A lion\'s head over a stone bowl, dark with old offerings of oil. Soldiers kneel here before a fight.',
        'Ingerimm': 'A soot-black altar with a hammer worn smooth by many hands.'}
for key, god, level, anchor, off, mods, text, stage in SHRINES:
    sid = f'LayBless{key}'
    L.timed_status(sid, f'Blessing of {god}', f'{text}. Granted at a wayside shrine; lasts about a quarter of an hour.', mods, 900,
                   texture='status_fx_good_jewel', categories='buff;good;blessing')
    use = L.action_script(f'{NS}_shrine_{key.lower()}_use.xml',
        L.for_party(lambda who: A('SetStatusEffect', who=who, id=sid)) +
        [A('PlayVisualEffect', effect='Balsam_Impact', target='Hero', fixedposition='false'),
         A('ShowOverHeadMessage', _sel='actionSelection="script"', msg=f'{god} smiles on the party.', who='Hero')])
    gate = L.condition_script(f'{NS}_shrine_{key.lower()}_can.xml', Not(C('HasStatusEffect', id=sid, who='Hero')))
    oid = f'{NS}_shrine_{key.lower()}'
    L.object(oid, f'Shrine of {god}', LORE[key], level, anchor, off, base='dun04_altarschale',
             graphics='_location_all_elements/altar', on_use=use, can_use=gate, picking=3.0)
    L.trigger(f'{oid}_hint', level, anchor, off, radius=6.0, filter='IsBeing;IsPartyLeader;',
              enter=A('ShowOverHeadMessage', _sel='actionSelection="script"', msg=f'A wayside shrine of {god}.', who='Hero') + ';')
    report.append(('Shrine', f'Shrine of {god}', level, f'{text} for 15 min (whole party); {stage}'))

# ============================================================== regrowing herbs + hunting grounds (level-enter scripts)
HERB_LEVELS = {'location03': 3, 'location04': 3, 'location05': 3, 'location08': 3, 'location10': 3}
HUNTS = {  # level: (our encounter, vanilla encounter whose ground we reuse, spawn list per spawn index)
    'location03': ('lay_hunt_darkforest', 'loc03_enc_holzfaeller_ueberfall',
                   [('Monster', 'Wolf'), ('Monster', 'Wolf'), ('Monster', 'Wolf_02'), ('Monster', 'Wolf_02'), ('Monster', 'Baer')]),
    'location08': ('lay_hunt_tallon', 'loc08_enc_rattelshof_woelfe_02',
                   [('Monster', 'Wildschwein'), ('Monster', 'Wildschwein'), ('Monster', 'Wolf_03'), ('Monster', 'Wolf_03'),
                    ('Monster', 'Wildschwein'), ('Monster', 'Baer02'), ('Monster', 'Wolf_03'), ('Monster', 'Wildschwein')]),
}
for level in sorted(set(HERB_LEVELS) | set(HUNTS)):
    items = []
    n = HERB_LEVELS.get(level, 0)
    if n:
        srcs = m.g.execute('select Guid, Id from _Instance_Herb where _Level=? order by Id, rowid', (level,)).fetchall()
        picked, seen = [], set()
        for g, hid in srcs:   # one patch per herb kind first, then more of the same
            if hid not in seen: picked.append((g, hid)); seen.add(hid)
        picked += [x for x in srcs if x not in picked]
        regrow = []
        for i, (g, hid) in enumerate(picked[:n]):
            regrow += L.herb_patch(f'{NS}_herb_{level}_{i + 1}', level, g)
            report.append(('Herb patch', hid, level, 'regrows every 3rd visit'))
        ctr = f'{NS}_herbs_{level}'
        items += [A('AddToCounter', counter=ctr, value=1),
                  ('if', C('CompareCounter', counter=ctr, operator='greaterOrEqual', value=3), [A('ResetCounter', counter=ctr)] + regrow)]
    if level in HUNTS:
        name, ground, spawns = HUNTS[level]
        pts = m.g.execute('select count(*) from _Instance_SpawnPoint where EncounterName=? and _Level=?', (ground, level)).fetchone()[0]
        spawns = spawns[:pts]
        L.encounter(name, level, ground, [L.spawn(i, c, t) for i, (c, t) in enumerate(spawns)], reactivate_after=1200.0, count=4, active=0)
        ctr = f'{NS}_visits_{level}'
        items += [A('AddToCounter', counter=ctr, value=1),
                  ('if', C('CompareCounter', counter=ctr, operator='greaterOrEqual', value=2), [A('SetTriggerActive', trigger=name, status='true')])]
        report.append(('Hunting ground', ', '.join(sorted({t for _, t in spawns})), level, 'from the 2nd visit; every 20 min, 4 times'))
    script = L.action_script(f'{NS}_enter_{level}.xml', items)
    L.on_level_enter(level, script)

# ============================================================== reactive presets: rally / frenzy
L.timed_status('LayRally', 'Last Stand', 'Badly hurt, this fighter throws everything into the attack: Attack +2, Parry +2.', 'AT +2 PA +2', 30,
               state_effect='Kampf_Offensiv1', hardpoint='Head', texture='status_fx_spell_kampfrausch', categories='buff')
L.timed_status('LayFrenzy', 'Frenzy', 'A wounded beast at bay: Attack +3, Parry -2.', 'AT +3 PA -2', 30,
               state_effect='Kampf_Offensiv1', hardpoint='Head', texture='status_fx_spell_kampfrausch', categories='buff')
for sid, script, pct, msg in (('LayRally', f'{NS}_on_damage_rally.xml', 0.33, 'Rallies!'), ('LayFrenzy', f'{NS}_on_damage_frenzy.xml', 0.25, 'Frenzied!')):
    L.action_script(script, [('if', And(C('HealthCritical', who='AimedEntity', percent=pct), Not(C('HasStatusEffect', id=sid, who='AimedEntity'))),
                              [A('SetStatusEffect', who='AimedEntity', id=sid),
                               A('ShowOverHeadMessage', _sel='actionSelection="script"', msg=msg, who='AimedEntity')])])
HOSTILE = ('FaFeind', 'FaRaubtier', 'FaHexen', 'FaLoc03_Raeuber', 'FaLoc03_Banditen', 'FaKultisten', 'FaLoc08Pluenderer', 'FaLoc08Barbar')
elite = [r for r in m.s.execute("select Id, LEmax from _Template_NPC where Behaviour='clever_fighter' and LEmax >= 30 and Id not like '%loc12%'")
         if m.s.execute('select Faction from _Template_NPC where Id=?', (r[0],)).fetchone()[0] in HOSTILE]
for tid, le in elite:
    L.attach_preset('NPC', tid, on={'DamageTaken': f'{NS}_on_damage_rally.xml'})
ANIMALS = ('Baer', 'Wildschwein', 'Wolf', 'Riesenkrabbe', 'Smaragdspinne', 'Spinne', 'Riesenskorpion', 'Trollkroete', 'Harpyie', 'Gruftassel')
beasts = [r for r in m.s.execute("select Id, LEmax, Faction from _Template_Monster where LEmax >= 40 and Faction in ('FaRaubtier','FaFeind','FaHexen') "
                                 "and Id not like '%loc12%' and Id not like 'summon%' and Id not like '%bossfight%' and Id not like '%_boss%'")
          if r[0].startswith(ANIMALS)]
for tid, le, fa in beasts:
    L.attach_preset('Monster', tid, on={'DamageTaken': f'{NS}_on_damage_frenzy.xml'})
report.append(('Last Stand', f'{len(elite)} elite fighters', 'everywhere but the final mountain', 'below 1/3 LE: AT +2 PA +2 for 30 s, once'))
report.append(('Frenzy', f'{len(beasts)} large beasts', 'everywhere but the final mountain', 'below 1/4 LE: AT +3 PA -2 for 30 s, once'))

# ============================================================== wolves: the unused howling pack behaviour
wolf = L.clone_machine('monster_wolf', f'{NS}_wolf_pack')
std_dead = Or(C('HasStatusEffect', id='wound', amount=5, everybody='true'), C('HealthCritical', value=0))
wolf.remove_transitions('Idle', 'Dead').transition('Idle', 'Dead', std_dead, index=0)   # vanilla wolves also die of 5 wounds
wolf.emit()
wolves = [r[0] for r in m.s.execute("select Id from _Template_Monster where (Id like 'Wolf%' or Id like '%_wolf%' or Id like 'wolf%') "
                                    "and Id not like 'Wolfsratte%' and Id not like 'summon%' and Behaviour='stupid_fighter'")]
for tid in wolves:
    L.set_behaviour('Monster', tid, wolf.id)
report.append(('Wolf pack', f'{len(wolves)} wolf kinds', 'everywhere', 'howl (calls the pack), then attack the nearest; machine monster_wolf'))

# ============================================================== ogre ground slam
L.action_script(f'{NS}_ogre_slam_hit.xml', [('if', C('IsPartyMember', who='AimedEntity'), [
    ('if', Not(C('Probe', who='AimedEntity', difficulty=4, attribute='KK', showProbe='true')),
     [A('SetStatusEffect', who='AimedEntity', id='overthrown')]),
    A('Hurt', who='AimedEntity', fixedDamage=2, dice=6, diceAmount=1, showNoDamage='false', damageType='physical')])])
L.action_script(f'{NS}_ogre_slam.xml', [A('PlayVisualEffect', effect='Funken_Big', target='ActingEntity', fixedposition='false'),
                                         A('RunActionScriptInRadius', who='ActingEntity', script=f'{NS}_ogre_slam_hit.xml', radius='4.0')])
L.script_attack('LayOgreSlam', 'Ground Slam', f'{NS}_ogre_slam.xml', 'The ogre pounds the ground: everyone close by may be knocked down (KK check).')
ogres = [r[0] for r in m.s.execute("select Id from _Template_NPC where Id like 'Oger%' and Faction='FaFeind' and SpecialAttackChances like 'OgerSweepAttack%'")]
for tid in ogres:
    L.add_attack_chance('NPC', tid, 'LayOgreSlam', 1.5)
report.append(('Ground Slam', f'{len(ogres)} ogre kinds', 'Tallon and later', '1 in ~8 attacks: KK+4 check or knocked down, 1d6+2 to the party within 4 m'))

# ============================================================== output
m.check_collisions()
m.write(out)
L.write_checks(out)
write_sync_bat(out, 'World Systems')
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
md = ['# World Systems (optional)', '',
      'New play built on the engine layers (`tools/layers.py`, `docs/ENGINE_ARCHITECTURE.md`). Install after the pack; uninstall restores',
      'exactly what it changed (every edit of a vanilla row is guarded: if another mod changed that row first, it is left alone).', '',
      '**New game recommended.** Shrines, herb patches, hunting grounds and placed wolves/ogres live in the world database; on an existing',
      'save only the static parts work (rally/frenzy, ground slam, howling for wolves spawned later) unless the save is synced with',
      '`tools/maint/sync_save_world.py`.', '',
      '| Feature | What | Where | Effect |', '|---|---|---|---|'] + [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in report] + [
      '', '## Status: needs an in-game test', '',
      'Built from vanilla patterns, checked offline (`python -I tools/maint/validate.py --mods world_systems`). Not yet seen in play:',
      '', '1. Shrine placement (2.5 m from the workbench; move with the offsets in `build_world_systems.py` if one stands in a wall).',
      '2. `can:Use` on an Object (vanilla uses it on items and workbenches).',
      '3. Regrowth timing (vanilla runs its player-house regrowth the same way).',
      '4. `ActingEntity` inside a ScriptCombatAction script (the ground slam). If nothing happens, see engine_lab probe P5.',
      '5. The revived wolf howl (animation `Idle_Howl`).', '']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('world_systems:', len(report), 'features,', len(m.static), 'static lines,', len(m.game), 'game lines')
