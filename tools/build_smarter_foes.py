"""Smarter Foes (optional module): enemy AI tuning through the game's own state machines (layers 3 and 4, tools/layers.py).

  * Human fighters (machine simple_fighter, ~1000 NPCs): pick targets like the game's "clever" fighters do: finish off the
    wounded, go for spellcasters and archers, prefer lightly armoured heroes (SelectTarget weights only).
  * Beasts and bandits (stupid_fighter): packs pile on a wounded hero (mild).
  * Bandits and robbers get their own machine: once per fight, below 20% LE, they run for a few seconds, then come back.

Static only: works on existing saves for every NPC that uses these machines, except the bandit machine, which is set on the
templates (spawned bandits) and on placed bandits in game.db4 (new game or synced save).
Usage: python -I tools/build_smarter_foes.py "<game>/export/db/armory_backup" mods/smarter_foes
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod
from layers import write_sync_bat, Layers, A, C, Not, And

db, out = sys.argv[1], sys.argv[2]
m = Mod(db, 'smarterfoes')
L = Layers(m)
report = []

HUMAN = ('liveEnergyWeighting="0" astralEnergyWeighting="0" armourWeighting="0" rangedWeighting="0"',
         'liveEnergyWeighting="-15" astralEnergyWeighting="15" armourWeighting="-10" rangedWeighting="10"')
BEAST = ('actualTargetWeighting="0" liveEnergyWeighting="0"', 'actualTargetWeighting="0" liveEnergyWeighting="-8"')
n = L.tune_machine('simple_fighter', dict([HUMAN]))
report.append(('simple_fighter', f'{n} statements', 'wounded -15, casters +15, armour -10, archers +10 (vanilla 0 / 0 / 0 / 0)'))
n = L.tune_machine('stupid_fighter', dict([BEAST]))
report.append(('stupid_fighter', f'{n} statements', 'wounded -8 (vanilla 0)'))

L.timed_status('LayFled', 'Fled', 'Ran from the fight once already.', '', 120, texture='status_fx_bad_poisoned', categories='bad')
bandit = L.clone_machine('stupid_fighter', 'lay_bandit', replace=dict([BEAST]))
flee = And(C('HealthCritical', percent=0.2), Not(C('HasStatusEffect', id='LayFled')), Not(C('HealthCritical', value=0)))
run = [A('SetStatusEffect', id='LayFled'), A('StartEscape', _sel='actionSelection="script"', fleeFromAll='true', duration=8)]
for st in ('SelectTarget', 'MeleeAttack', 'RangeAttack'):
    bandit.transition(st, 'Escape', flee, actions=run, index=0)
bandit.emit()
HOSTILE = ('FaFeind', 'FaLoc03_Raeuber', 'FaLoc03_Banditen', 'FaLoc08Pluenderer')
bandits = [r[0] for r in m.s.execute("select Id, Faction from _Template_NPC where (Id like 'Raeuber%' or Id like '%raeuber%' or Id like '%bandit%' "
                                     "or Id like '%pluenderer%') and Behaviour='stupid_fighter'") if r[1] in HOSTILE]
for tid in bandits:
    L.set_behaviour('NPC', tid, 'lay_bandit')
report.append(('lay_bandit', f'{len(bandits)} bandit/robber kinds', 'stupid_fighter + flee once below 20% LE for 8 s'))

m.check_collisions()
m.write(out)
L.write_checks(out)
write_sync_bat(out, 'Smarter Foes')
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
md = ['# Smarter Foes (optional)', '', 'Enemy AI tuning through the game\'s own state machines (see `docs/ENGINE_ARCHITECTURE.md` section 6).',
      'Every edit is a guarded change of one vanilla statement; Uninstall restores the exact text.', '',
      '| Machine | Scope | Change |', '|---|---|---|'] + [f'| {a} | {b} | {c} |' for a, b, c in report] + [
      '', 'Works on existing saves (the machines are static data), except the bandit machine on bandits already placed in a save.',
      '', '## Status: needs an in-game test', '', '1. Target choice of human enemies (they should go for the mage and the wounded).',
      '2. Bandits fleeing (StartEscape inside a transition: vanilla uses StartEscape in a state; the transition statement block is',
      '   the same mechanism vanilla uses 3 times).', '']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('smarter_foes:', report)
