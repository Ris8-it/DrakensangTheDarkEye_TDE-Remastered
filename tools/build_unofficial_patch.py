"""Unofficial Patch (optional): fixes for broken references in the vanilla data, found by the research atlas
(docs/db-atlas "Dangling references", nearest-key column) and checked one by one.

  * Big wolves, big emerald spiders and big troll toads drop nothing: their LootTable names `loot_*_groß`, but vanilla
    stored the tables as `loot_wolf_großo`, `loot_smaragdspinne_groß?`, `loot_trollkroete_groß?` (stray characters).
    The correctly named tables are added with the same content.
  * Light skeleton archers name `loot_skelett_leicht_fern`, which does not exist: added as a copy of
    `loot_skelett_leicht_fern_bogen` (they carry a composite bow).
  * Two emerald spiders of the orc fight in the castle vaults name preset `preset_on_hurt_swap_target.xml` (typo of
    `preset_on_hit_swap_target.xml`, which the orc of the same fight uses): the missing name is added as an alias.
  * Two idle routines are misspelled (`loc03_ba_berndrich_wache.xml` for `lo03_...`, `..._runde_02xml` for `..._02.xml`):
    the Praios guard at the pond and a Tallon townswoman stood still. Corrected on template and placed instance.
  * 11 description texts that vanilla never wrote (9 chests, 2 orcish war dogs) are added.

Every change is guarded: a row a previous mod already fixed or changed is left alone. Static fixes reach existing saves;
the placed guard's routine needs a new game or SyncSave.bat.
Usage: python -I tools/build_unofficial_patch.py "<game>/export/db/armory_backup" mods/unofficial_patch
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, insert, lit
from layers import Layers, write_sync_bat

db, out = sys.argv[1], sys.argv[2]
m = Mod(db, 'unofficialpatch')
L = Layers(m)
fixes = []
tables = {r[0]: (r[1], r[2]) for r in m.s.execute('select LootTableName, LootTableValue, LootTableContent from _DSA_LootTables')}

# ---- loot tables (names compared as decoded cp1252 text; the SQL file is written in cp1252, so 'ß' is the byte DF again)
LOOT = [('loot_wolf_groß', 'loot_wolf_großo'), ('loot_smaragdspinne_groß', 'loot_smaragdspinne_groß?'),
        ('loot_trollkroete_groß', 'loot_trollkroete_groß?'), ('loot_skelett_leicht_fern', 'loot_skelett_leicht_fern_bogen')]
for want, have in LOOT:
    if want in tables or have not in tables:
        print('skip loot', want, '(already present or source missing)')
        continue
    users = [r[0] for r in m.s.execute('select Id, LootTable from _Template_Monster union all select Id, LootTable from _Template_NPC')
             if r[1] == want]
    v, c = tables[have]
    m.static += [f'-- loot table {want} (copy of the misnamed or nearest vanilla table)',
                 f'DELETE FROM _DSA_LootTables WHERE LootTableName={lit(want)};',
                 insert('_DSA_LootTables', dict(LootTableName=want, LootTableValue=v, LootTableContent=c))]
    m.undo_static.append(f'DELETE FROM _DSA_LootTables WHERE LootTableName={lit(want)};')
    L.checks_static.append((f'loot table {want.encode("ascii", "replace").decode()}',
                            f'SELECT count(*) FROM _DSA_LootTables WHERE LootTableName={lit(want)}', 1))
    fixes.append(('Loot', f'`{want}` (copy of `{have}`)', f'{len(users)} templates: ' + ', '.join(users[:6]) + (' ...' if len(users) > 6 else '')))

# ---- preset typo
if not m.s.execute("select 1 from _DSA_Preset where PresetName='preset_on_hurt_swap_target.xml'").fetchone():
    L.preset('preset_on_hurt_swap_target.xml', base='preset_on_hit_swap_target.xml')
    users = [r[0] for r in m.s.execute("select Id from _Template_Monster where ScriptPreset='preset_on_hurt_swap_target.xml'")]
    fixes.append(('Preset', '`preset_on_hurt_swap_target.xml` = alias of `preset_on_hit_swap_target.xml`', ', '.join(users)))

# ---- idle routine typos
ROUTINES = {'loc03_ba_berndrich_wache.xml': 'lo03_ba_berndrich_wache.xml',
            'loc08_ba_tallon_belebung_friedhof_runde_02xml': 'loc08_ba_tallon_belebung_friedhof_runde_02.xml'}
acts = {r[0] for r in m.s.execute('select ScriptName from _Scripts_ActionScripts')}
for bad, good in ROUTINES.items():
    assert good in acts and bad not in acts, (bad, good)
    for (tid,) in m.s.execute('select Id from _Template_NPC where BaseActionScript=?', (bad,)).fetchall():
        L.guarded_update('static', '_Template_NPC', {'Id': tid}, 'BaseActionScript', good, bad)
        fixes.append(('Idle routine', f'`{bad}` → `{good}`', f'template {tid}'))
    for g, name in m.g.execute('select Guid, Name from _Instance_NPC where BaseActionScript=?', (bad,)).fetchall():
        L.guarded_update('game', '_Instance_NPC', {'Guid': g}, 'BaseActionScript', good, bad)
        fixes.append(('Idle routine', f'`{bad}` → `{good}`', f'placed NPC {name}'))

# ---- missing description texts
TEXTS = {
    'infoid_loc02_spielerhaus_werkbank_kiste': 'A sturdy crate for tools and materials.',
    'infoid_loc02_spielerhaus_werkbank_truhe': 'A chest beside the workbench, for whatever is worth keeping.',
    'infoid_loc03_truhe_da_vanya': 'A well-made travelling chest, bound in iron.',
    'infoid_loc03_truhe_ronkwer': 'A battered chest that has seen a lot of hard use.',
    'infoid_loc03_truhe_humpert': 'A plain wooden chest.',
    'infoid_loc03_truhe_saphira': 'A small chest, carefully kept.',
    'infoid_loc03_truhe_guthof': 'A farmhouse chest of dark oak.',
    'infoid_loc03_truhe_koch': 'A greasy chest that smells of the kitchen.',
    'infoid_loc03_truhe_danor': 'A heavy chest with a solid lock.',
    'infoid_Kampfhund_loc05_orks_innen_pat1': None, 'infoid_Kampfhund_loc05_orks_innen_pat2': None,
}
dog = m.l.execute("select LocaText from _Locale where LocaId='infoid_Kampfhund'").fetchone()[0]
for k, v in TEXTS.items():
    if m.l.execute('select 1 from _Locale where LocaId=?', (k,)).fetchone():
        continue
    used = m.s.execute('select count(*) from _Template_Chest where InfoIdentified=?', (k,)).fetchone()[0] + \
        m.s.execute('select count(*) from _Template_Monster where InfoIdentified=?', (k,)).fetchone()[0]
    assert used, k
    m.text(k, v or dog)
fixes.append(('Texts', f'{len([k for k in TEXTS if k in m.locale])} missing description texts', '9 chests, 2 orcish war dogs'))

m.write(out)
L.write_checks(out)
write_sync_bat(out, 'Unofficial Patch')
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
md = ['# Unofficial Patch (optional)', '', 'Fixes for broken references in the vanilla data (missing loot, misspelled script names, missing texts).',
      'Found by the research database atlas (dangling references with a nearest existing key) and checked one by one.',
      'Every change is guarded and undone exactly by Uninstall.bat.', '', '| Fix | What | Affects |', '|---|---|---|'] + \
     [f'| {a} | {b} | {c} |' for a, b, c in fixes] + [
      '', 'Loot, preset and texts are static data: they work on existing saves (monsters already placed in a save keep their',
      'own LootTable name, which is the same broken name, so they also drop loot now). The guard\'s idle routine is a placed',
      'instance: new game, or SyncSave.bat.', '',
      'Not changed (needs an in-game test first): Behaviour `basic_monster` on three cave troll toads (the machine does not',
      'exist; what the game does with it is unknown), and sound cues whose names differ from the sound objects.', '']
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('unofficial_patch:', len(fixes), 'fixes')
