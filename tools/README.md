# Tools

All scripts take the DB folder as first argument, e.g.
`python -I tools/build_saber.py "D:/Steam/steamapps/common/Drakensang/export/db" <out_dir>`

- `build_saber.py` — reference generator: clones a vanilla weapon template + merchant instance, writes idempotent install/undo SQL (Ravenwing Saber).
- `build_test.py` — puts an item into Rhulana's starting backpack (test pattern).
- `build_phase0.py` — Phase 0 test pack: `Block` builder for vanilla-shaped scripts (If/Then/Condition rows, .NET GUID refs), permanent status effects, Weapon/Jewelry/Armor clones into Rhulana's pack, DXT3+mips icon, idempotent install/undo/verify SQL.
- `research/` — read-only probes used to map the engine:
  - `decode1.py <db> <ScriptName...>` fully decodes an action script (every Statement/Condition row, raw GUIDs); `decode2.py <db> <PeId...>` the same for status-effect scripts
  - `script.py` decodes status-effect and on-hit scripts into readable statements
  - `research*.py` action verbs, visual effects, conditions, debuffs, prices, party, loot tables
  - `cano3.py` / `ergo.py` list what a merchant stocks and verify counts
- `layers.py` — generators for the 18 engine layers (docs/ENGINE_ARCHITECTURE.md §11/§13): presets, can: gates, AI state machines (clone/edit/tune),
  scripted attacks, level-enter scripts, triggers, zones, heartbeats, objects, service points, encounters, probes, factions, area hazards,
  new categories, new columns. `loosefiles.py` builds loose data/tables/*.xml patches from the player's own archives.
- `build_world_systems.py`, `build_smarter_foes.py`, `build_engine_lab.py` — the optional modules and the in-game test pack built with them.
- `engine/` — read-only decoders: `dsa_script.py` (scripts, condition scripts, status effects, AI machines, quests as pseudo-code), `vocab.py`
  (every verb/atom/event with counts), `engine_map.py` (property/attribute glossaries), `xltable.py` (Excel-XML tables), `save_diff.py` (what a save holds).
- `maint/sqlrun.py <db folder> <mod> install|uninstall|verify` — run a module's SQL anywhere (Python fallback writes the same bytes as sqlite3.exe).
- `build_unofficial_patch.py` — vanilla data fixes (misnamed loot tables, misspelled preset and idle routines, missing texts), all guarded.
- `engine/dsa_script.py` treats a top condition row with several children as AND (vanilla does this in 339 scripts).
