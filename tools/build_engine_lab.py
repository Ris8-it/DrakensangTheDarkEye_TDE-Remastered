"""Engine Lab: the in-game test pack for every engine layer that the data alone cannot prove (like the Phase 0 packs).

Install on a TEST copy of the game (or a throwaway profile), start a NEW game; Rhulana carries numbered "Lab" items. Use each one
and write down what you see; LAB_TESTS.md (generated next to this module) is the checklist. Some probes may assert: save first.

Stage 1 (mods/engine_lab): probes P01-P20, lab objects at the Avestrue start, lab faction/attribute/ability columns, loose-file
patch spec (effects.xml alias + blueprints.xml additions) applied with LooseFiles_Install.bat.
Stage 2 (mods/engine_lab_stage2): a brand-new entity category with one instance at the Avestrue start. Install ONLY after
probe P12 showed that loose data files load (otherwise the level aborts: "category not found in blueprints.xml").

Usage: python -I tools/build_engine_lab.py "<game>/export/db/armory_backup" mods/engine_lab mods/engine_lab_stage2
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod
from layers import Layers, A, C, Not, And, Or
import loosefiles

db, out, out2 = sys.argv[1], sys.argv[2], sys.argv[3]
m = Mod(db, 'enginelab')
L = Layers(m)
LVL, START = 'location01', ('Entry', 'Loc01_Entry_Start')
SAY = lambda msg, who='Hero': A('ShowOverHeadMessage', _sel='actionSelection="script"', msg=msg, who=who)
tests = []   # (probe, layer, what to do, what to expect, question answered)
BASE_ITEM = 'special_hellesferdoker'   # usable drink with on:Use and no preset; CanDestroy 0 keeps the probe reusable

def probe(n, title, layer, todo, expect, question, items, risky=False):
    iid = f'lab_p{n:02d}'
    script = L.action_script(f'{iid}.xml', items)
    L.probe_item(iid, f'Lab {n:02d}: {title}', f'Engine lab probe ({layer}). {todo}', script, base=BASE_ITEM)
    tests.append((f'P{n:02d}', title, layer, todo, expect, question, risky))

# ---------------------------------------------------------------- shared lab content
RH_WEAPON = m.g.execute("select Id from _Instance_Weapon where StorageGUID=(select Guid from _Instance_PC where Name='Rhulana') order by rowid").fetchone()[0]
L.timed_status('LayLabPulseMark', 'Lab: pulse running', 'Engine lab marker.', '', 40, categories='buff')
L.heartbeat('LayLabPulse', 'Lab: heartbeat', 'Engine lab: says "pulse" every 5 seconds, 6 times.', 5,
            [SAY('Lab: pulse'), ('if', C('IsPartyMember', who='Rhulana'), [SAY('Lab: pulse (Rhulana in party)', 'Rhulana')])], times=6)
coin = 'lab_coin'
m.template('Item', 'special_seife', coin, 'Lab Coin', 'Engine lab token. Used by probes P05 and P15.', Value=0, ScriptOverride='', ScriptPreset='')
L.condition_script('lab_has_coin.xml', C('IsInInventory', category='Item', templateId=coin))
# zone: three markers around the start (P13)
edges = []
for i, off in enumerate(((6, 0, 6), (6, 0, -6), (-6, 0, 0))):
    edges.append(L.marker(f'lab_zone_{i + 1}', LVL, START, off)['Name'])
# lab altar with a can: gate (P16/P17) and a trigger next to it (P18)
L.action_script('lab_altar_use.xml', [SAY('Lab: altar used (on:Use on an Object works)')])
L.condition_script('lab_altar_can.xml', Not(C('HasStatusEffect', id='LayLabPulseMark', who='Hero')))
L.object('lab_altar', 'Lab Altar', 'Engine lab test object.', LVL, START, (3.0, 0, 3.0), graphics='_location_all_elements/altar',
         on_use='lab_altar_use.xml', can_use='lab_altar_can.xml')
L.trigger('lab_trigger', LVL, START, (3.0, 0, 3.0), radius=3.0, once=False, one_way=False, filter='IsBeing;IsPartyLeader;',
          enter=SAY('Lab: trigger entered') + ';', leave=SAY('Lab: trigger left') + ';')
# level-enter script (P19)
L.action_script('lab_enter_location01.xml', [A('AddToCounter', counter='lab_enter', value=1), SAY('Lab: level-enter script ran'),
    ('if', C('CompareCounter', counter='lab_enter', operator='greaterOrEqual', value=2), [SAY('Lab: ...and this is not the first entry')])])
L.on_level_enter(LVL, 'lab_enter_location01.xml')
# faction + lab rat with DamageTaken token probe (P10, P20)
L.faction('FaLayLab', 'Lab faction', {'FaPlayer': 'Hostile'})
L.action_script('lab_rat_hurt.xml', [SAY('Lab: I am AimedEntity (the one hurt)', 'AimedEntity'), SAY('Lab: I am ActingEntity (the attacker)', 'ActingEntity')])
L.preset('lab_preset_rat.xml', on={'DamageTaken': 'lab_rat_hurt.xml', 'Death': 'lab_rat_death.xml'})
L.action_script('lab_rat_death.xml', [SAY('Lab: on:Death ran', 'Hero')])
L.clone_template('Monster', 'Wolfsratte_loc01', 'lab_rat', Name='lab_rat', Faction='FaLayLab', ScriptPreset='lab_preset_rat.xml', BaseActionScript='',
                 LootTable='', SetupStorage='')
# custom attribute on the hero (P07) and a learnable scripted maneuver (P08)
L.add_column('game', '_Instance_PC', 'LayLabValue', 'INTEGER', default=0)
L.add_column('static', '_Template_PC', 'LayLabValue', 'INTEGER', default=0)
L.special_ability('SF_LayLabStrike')
L.action_script('lab_strike.xml', [SAY('Lab: scripted maneuver ran', 'ActingEntity'),
                                   A('Hurt', who='AimedEntity', fixedDamage=1, dice=6, diceAmount=1, showNoDamage='false', damageType='physical')])
L.script_attack('LayLabStrike', 'Lab Strike', 'lab_strike.xml', 'Engine lab: a scripted maneuver (Game::ScriptCombatAction) for heroes.',
                AtAttr='SF_LayLabStrike', AttrCategory='CloseCombat', IconBrush='icons/spec_attack', SkillRequirements='', XP=0, AU=2)
m.game.append("UPDATE _Instance_PC SET SF_LayLabStrike=1 WHERE Name='Rhulana';")   # column is removed by the undo rebuild
# area hazard (P11)
L.action_script('lab_hazard_tick.xml', [SAY('Lab: hazard tick', 'AimedEntity')])
hazard = L.area_hazard('lab_hazard', 'lab_hazard_tick.xml')
# scripted area hit from an item, token check (P06)
L.action_script('lab_radius_mark.xml', [SAY('Lab: inside the radius (AimedEntity)', 'AimedEntity')])

# ---------------------------------------------------------------- probes
probe(1, 'IsEquipped', 'layer 13 (unused designer atom)', 'Use with Rhulana\'s starting weapon equipped, then unequipped.',
      'Two different messages: "equipped: yes/no". An assert = the atom does not exist.', 'Does IsEquipped exist (fills the "no is-equipped atom" gap)?',
      [('if', C('IsEquipped', item=RH_WEAPON), [SAY('Lab: IsEquipped -> yes')], [SAY('Lab: IsEquipped -> no')])], risky=True)
probe(2, 'IsItemAddable', 'layer 13', 'Use once.', '"addable: yes/no". An assert = missing atom.', 'Does IsItemAddable exist?',
      [('if', C('IsItemAddable', category='Item', templateId=coin), [SAY('Lab: IsItemAddable -> yes')], [SAY('Lab: IsItemAddable -> no')])], risky=True)
probe(3, 'IsDialogUnLocked', 'layer 13', 'Use once.', '"unlocked: yes/no".', 'Does IsDialogUnLocked exist?',
      [('if', C('IsDialogUnLocked', dialog='AlweneDialog'), [SAY('Lab: IsDialogUnLocked -> yes')], [SAY('Lab: IsDialogUnLocked -> no')])], risky=True)
probe(4, 'IsSubTaskUnLocked', 'layer 13', 'Use once.', '"subtask: yes/no".', 'Do the IsSubTask* atoms exist?',
      [('if', C('IsSubTaskUnLocked', quest='Einladung_nach_Ferdok', task='2_Fuersprecher', subtask='Salina'), [SAY('Lab: IsSubTaskUnLocked -> yes')],
        [SAY('Lab: IsSubTaskUnLocked -> no')])], risky=True)
probe(5, 'AddItem', 'layer 13 (unused designer verb)', 'Use once, open the inventory.', 'A "Lab Coin" appears.', 'Does AddItem exist?',
      [A('AddItem', category='Item', templateId=coin), SAY('Lab: AddItem sent')], risky=True)
probe(6, 'ActingEntity radius script', 'layers 5/8', 'Stand next to Rhulana and Dranor, use.', 'Every hero within 6 m says "inside the radius".',
      'Does RunActionScriptInRadius who="ActingEntity" work (the ogre Ground Slam relies on it)?',
      [A('RunActionScriptInRadius', who='ActingEntity', script='lab_radius_mark.xml', radius='6.0')])
probe(7, 'Custom attribute', 'layer 18 (new column)', 'Use 3 times, save, then inspect the save with tools/engine/save_diff.py or sqlite.',
      '_Instance_PC.LayLabValue of the hero = 3.', 'Does ModifyAttribute accept an attribute declared only in _Attributes + a new column?',
      [A('ModifyAttribute', _sel='actionSelection="script"', modifier='LayLabValue +1', who='Hero'), SAY('Lab: LayLabValue +1 sent')], risky=True)
probe(8, 'Hero scripted maneuver', 'layer 5', 'Open Rhulana\'s special attacks (she knows SF_LayLabStrike), use "Lab Strike" on an enemy.',
      'The maneuver is listed; using it shows "scripted maneuver ran" and hits for 1d6+1.', 'Can heroes learn/use a Game::ScriptCombatAction?',
      [SAY('Lab: P08 is tested in combat: look for "Lab Strike" in Rhulana\'s special attacks')])
probe(9, 'Heartbeat', 'layer 9', 'Use once with Rhulana in the party, once without.',
      '"pulse" 6 times, 5 s apart; with Rhulana also her line (If inside a status block, with the automatic Else).',
      'Do unrolled status-effect loops with If/Else run?', [A('SetStatusEffect', who='Hero', id='LayLabPulse'),
                                                             A('SetStatusEffect', who='Hero', id='LayLabPulseMark')])
probe(10, 'Lab faction', 'layer 15', 'Use: a rat of the new faction FaLayLab appears next to the hero.',
      'It attacks (FaLayLab is hostile to the player). P20 uses it too.', 'Does a faction added as a new column work?',
      [A('CreateEntity', category='Monster', templateId='lab_rat', how='spawnAtEntity', entity='Hero'), SAY('Lab: lab rat sent')], risky=True)
probe(11, 'Area hazard', 'layer 16', 'Use: a cloud appears at the hero.', 'Heroes inside say "hazard tick" (InsideActions of a new AreaSpellTrigger).',
      'Can scripts create AreaSpellTrigger entities with their own scripts?', [hazard('Hero'), SAY('Lab: hazard sent')], risky=True)
probe(12, 'Loose effects.xml', 'layer 14', 'First run LooseFiles_Install.bat, restart the game, use.', 'A Balsam glow at the hero (effect alias LayLabGlow).',
      'Do loose data/tables/*.xml files override the archives?', [A('PlayVisualEffect', effect='LayLabGlow', target='Hero', fixedposition='false'),
                                                                  SAY('Lab: LayLabGlow played')], risky=True)
probe(13, 'Zone', 'layer 8', 'Use inside the triangle of lab markers right at the start, then far away.', '"in zone" vs "outside".',
      'Does IsInside with MarkerPoint edges work for scripts?', [('if', L.inside('Hero', edges), [SAY('Lab: in zone')], [SAY('Lab: outside the zone')])])
probe(14, 'LockTask', 'layer 13', 'Use once; open the journal.', 'Message; the lab task (P14) shows as locked or nothing changes.',
      'Do LockTask/LockQuest exist?', [A('LockTask', quest='lab_quest', task='lab_task'), SAY('Lab: LockTask sent')], risky=True)
probe(15, 'Watcher', 'layer 9', 'Use P15, then P05 (AddItem) or drop/pick up a Lab Coin.', '"watcher fired" once the coin is in the inventory.',
      'Does WaitForCondition wait for a condition script?', L.watcher('lab_has_coin.xml', [SAY('Lab: watcher fired (coin found)')]))
probe(16, 'Altar gate', 'layers 2/10', 'Use the Lab Altar next to the start (3 m). Then use P09 (40 s mark) and try the altar again.',
      'First "altar used"; during the pulse mark the altar cannot be used.', 'Do on:Use and can:Use work on an Object?', [SAY('Lab: walk to the Lab Altar')])
probe(17, 'Level enter', 'layer 6', 'Leave Avestrue (any exit) and come back twice.', '"level-enter script ran" on every entry, plus "not the first" from the 2nd.',
      'Does a mod-added LevelEnterScript run on every entry?', [SAY('Lab: leave and re-enter Avestrue')])
probe(18, 'Trigger', 'layer 7', 'Walk onto the Lab Altar and away again.', '"trigger entered"/"trigger left" every time.', 'Do new trigger volumes fire (and re-fire)?',
      [SAY('Lab: walk over the Lab Altar spot')])
probe(19, 'Blueprint patch', 'layer 17', 'After LooseFiles_Install.bat: reach a large monster (Tallon).', 'Large monsters show a health bar.',
      'Does a loose blueprints.xml load?', [SAY('Lab: P19 is checked at a large monster')])
probe(20, 'DamageTaken tokens', 'layer 1', 'Use P10, hit the lab rat.', 'The rat says "AimedEntity", the attacker says "ActingEntity"; on death "on:Death ran".',
      'Which token is the victim in an on:DamageTaken script?', [SAY('Lab: hit the lab rat from P10')])
from quests import Story
st = Story(m, 'enginelab')
st.task('lab_quest', 'Engine Lab', 'Engine lab test quest.', 'closed', state='unlocked')
st.task('lab_task', 'Engine Lab task', 'Engine lab test task (P14).', 'closed', parent='lab_quest', state='unlocked')

m.check_collisions()
m.write(out)
L.write_checks(out)
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
LOOSE = {'id': 'engine_lab', 'patches': [
    {'file': 'data/tables/effects.xml', 'sheet': 'Tabelle1', 'rows': [['LayLabGlow', 'effects/balsam', 15, 0, 'TDE-Remastered engine lab']]},
    {'file': 'data/tables/blueprints.xml', 'properties': {'MonsterLarge': ['HealthBarGraphicsProperty']},
     'entities': {'LayLabShrine': ['PhysicsProperty', 'GraphicsProperty', 'LookProperty', 'Useable', 'ScriptProperty', 'LevelSwitchableProperty']}}]}
loosefiles.write_module_files(LOOSE, out)

# ---------------------------------------------------------------- stage 2: new category with one instance
m2 = Mod(db, 'enginelab2')
L2 = Layers(m2)
L2.category('LayLabShrine', 'Object')
t = dict(m2.s.execute("select * from _Template_Object where Id='dun04_altarschale'").fetchone())
t.update(Id='lab_shrine', Name='lab_shrine', LookAtText='lookat_lab_shrine', Graphics='_location_all_elements/altar', Physics='_location_all_elements/altar',
         CanUse=1, ScriptOverride='on:Use:lab_altar_use.xml')
from dsa import insert, lit
from layers import xform
m2.static += [insert('_Template_LayLabShrine', t)]
m2.text('lookat_lab_shrine', 'Lab Shrine (new category)')
p = L2.anchor_pos(LVL, START)
icols = [c[1] for c in m2.g.execute('pragma table_info(_Instance_Object)')]
row = {c: t.get(c) for c in icols if c in t}
from dsa import U
row.update(Guid=U('enginelab2', 'shrine').bytes, _ID='|Level|Objects|LayLabShrine|lab_shrine', _Level=LVL, _Layers='', Transform=xform((p[0] - 3, p[1], p[2] - 3)))
m2.game += [insert('_Instance_LayLabShrine', row)]
m2.write(out2)
L2.write_checks(out2)
os.makedirs(os.path.join(out2, 'icons'), exist_ok=True)
open(os.path.join(out2, 'icons', 'files.txt'), 'w').write('')

# ---------------------------------------------------------------- checklist
md = ['# Engine Lab (test pack, not for normal play)', '',
      'Install on a test copy of the game, start a NEW game. Rhulana carries the numbered Lab items (reusable). Use each, note what you see.',
      '"Risky" probes test words the vanilla game never uses: an engine assertion is a valid answer (= not supported). **Save before each.**',
      'Afterwards: Uninstall.bat (and LooseFiles_Uninstall.bat). Stage 2 (`mods/engine_lab_stage2`) only after P12 passed.', '',
      '| Probe | Layer | Do | Expect | Answers | Risky |', '|---|---|---|---|---|---|'] + \
     [f'| {p} {t} | {lay} | {todo} | {exp} | {q} | {"yes" if r else ""} |' for p, t, lay, todo, exp, q, r in tests] + [
      '', '## Stage 2: new category', '', 'After P12 passed (loose files load) and with LooseFiles_Install.bat applied: install `engine_lab_stage2`, start a new',
      'game. A second altar ("Lab Shrine (new category)") stands 3 m on the other side of the start. If Avestrue loads and it can be used,',
      'layer 18 works: new entity categories are possible from data. If the level aborts, uninstall stage 2.', '',
      '## Report back', '', 'For each probe: pass / fail / assert text. Results go into docs/ENGINE_REFERENCE.md §9 like the Phase 0 results.', '']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
open(os.path.join(out2, 'README.md'), 'w', encoding='utf-8').write('# Engine Lab stage 2\n\nNew entity category `LayLabShrine` with one instance at the Avestrue start. '
    'Needs mods/engine_lab installed AND its LooseFiles_Install.bat applied (the blueprint entry). See mods/engine_lab/README.md.\n')
print('engine_lab:', len(tests), 'probes')
