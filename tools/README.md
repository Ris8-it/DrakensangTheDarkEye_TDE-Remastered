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
