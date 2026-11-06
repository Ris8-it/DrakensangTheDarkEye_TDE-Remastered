"""Rebuild every module of Drakensang TDE - Remastered from the clean baseline, in dependency order, then test it.

    python -I tools/build_all.py            build all + run tools/maint/validate.py
    python -I tools/build_all.py --no-test  build only

Order matters: secret_quests reads the SQL of armory_v2 and remastered_systems; quest_avestrue uses both item sets.
The baseline is <game>/export/db/armory_backup (vanilla + the user's own earlier mods, before this pack).
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
BASE = os.path.join(GAME, 'export', 'db', 'armory_backup')
STEPS = [('build_armory.py', 'armory_v2'), ('build_arcane_thief.py', 'arcane_thief'), ('build_remastered.py', 'remastered_systems'),
         ('build_quest_avestrue.py', 'quest_avestrue'), ('build_secret_quests.py', 'secret_quests'), ('build_hard_ending.py', 'hard_ending'),
         # optional engine-layer modules (tools/layers.py): independent of the pack, built from the same baseline
         ('build_world_systems.py', 'world_systems'), ('build_smarter_foes.py', 'smarter_foes'), ('build_engine_lab.py', 'engine_lab mods/engine_lab_stage2')]
for script, mod in STEPS:
    outs = [os.path.join('mods', mod.split()[0])] + mod.split()[1:]
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, script), BASE, *outs], cwd=ROOT, capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.strip()][-1:] or ['']
    print(f'{mod:20} {"OK " if r.returncode == 0 else "FAILED"} {last[0][:110]}')
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:]); sys.exit(1)
if '--no-test' not in sys.argv:
    sys.exit(subprocess.run([sys.executable, '-I', os.path.join(HERE, 'maint', 'validate.py')], cwd=ROOT).returncode)
