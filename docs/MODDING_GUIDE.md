# Modding Drakensang: a practical guide

What we learned building *Drakensang TDE - Remastered*, in the order you'll need it. Details and proofs are in
`ENGINE_REFERENCE.md`; this is the path through it.

## 1. How the game stores things

- `export/db/static.db4`: templates. Every item, monster, NPC, recipe, status effect, loot table, dialogue and quest is a row
  (`_Template_Weapon`, `_Template_Monster`, `_DSA_LootTables`, `_Story_Dialogs`, `_Story_Tasks`, ...). Scripts are rows too.
- `export/db/locale.db4`: every visible text in `_Locale(LocaId, LocaText)`, cp1252. Items use `lookat_<id>` and `infoid_<id>` keys.
- `export/db/game.db4`: the starting world. `_Instance_*` rows place things in levels: a chest's items, a merchant's stock (rows
  whose `StorageGUID` is the owner's `Guid`, plus the owner's `StorageContentCount`), placed monsters and NPCs.
- Loose files in `export/textures/icons/*.dds` override the `.npk` archives (128x128 DXT3, no mipmaps).
- A save (`Documents/Drakensang/.../*.dsa`) is a SQLite copy of the world as played. It does NOT pick up new placed content;
  templates and texts come from the installed databases.

Never patch `drakensang.exe`: the Steam DRM refuses to start.

## 2. Making a module

1. Write a generator in `tools/` that opens the clean databases read-only and creates a `dsa.Mod`:
   ```python
   m = Mod(db, 'mymod')                                   # namespace for deterministic GUIDs
   m.template('Weapon', 'Saebel', 'my_saber', 'Saber of Wit', 'Flavour text', WpATmod=1, Value=500)   # clone + override
   m.place('Weapon', 'my_saber', 'npc', 'Haendler_3_loc02_haendler_praios_waffen', 'location02_praios')   # merchant stock
   m.loot('loot_some_table', 'Weapon', 'my_saber', mode='all')                                           # or a loot drop
   m.write(out)                                           # writes sql/{static,locale,game}.sql, undo_*.sql, verify_*.sql
   ```
2. Quests and characters: `quests.Story(m, 'mymod')` gives `npc()`, `dialog()`, `task()`, `monster()`, `loot_table()`, `stock()`.
   Characters who should appear later: `npc(..., park=True)` and the `arrive(nid)` action.
3. Installers: `python -I tools/make_bats.py mods/mymod mymod_backup "One-line description"`.
4. Test: add the module to `MODS` in `tools/maint/validate.py` (and `tools/build_all.py`), run it, expect `RESULT: ALL GOOD`.

## 3. Rules that save you hours

- **Clone, don't invent.** Copy a working vanilla row (item, script, dialogue) and change little. The engine is unforgiving about
  structure and silent about why.
- **Effect ids letters and digits only.** An underscore in a permanent-effect id breaks every tooltip of that item.
- **cp1252 everywhere.** Some loot table names contain 'ß'; match them through a decoded cache, never as a query parameter.
- **Guaranteed drops:** put them in the monster template's `SetupStorage`. A loot table with pick count 0 may skip entries.
- **Reusable tools** need a `CanDestroy 0` base (the Locksmith knife, not the hair pin).
- **Saves:** never write Python `bytes` into a TEXT column; never remove a recipe the party may have learned (`_PartyReceipes`)
  without remapping it; edit saves only with the game closed, and always the newest one.
- **Test in the game what the database can't prove.** A clean install proves the data is consistent, not that the engine likes it.

## 4. Tools you get

| Tool | Use |
|---|---|
| `tools/build_all.py` | rebuild everything + full test |
| `tools/maint/validate.py` | full offline test only (`--spoilers` also lists texts naming later places) |
| `tools/maint/save_doctor.py` | `check` / `fix` / `find <text>` on saves |
| `tools/maint/sync_save_world.py` | give an existing save the new placed content of a build |
| `tools/research/*.py`, `tools/npk.py` | read-only exploration of tables and archives |
| `tools/art/split_sheet.py` | cut a sheet of icons into single icons; `batch_remastered.py post` turns them into game icons |

## 5. Where to look things up

- Level names and story order: `DESIGN_RULES.md` §1. Item, effect and condition vocabulary: `ENGINE_REFERENCE.md` §3-5.
- NPCs, dialogue and quest tables: `ENGINE_REFERENCE.md` §11. Save and loot lessons: §12.
- A worked example of everything at once: `tools/build_secret_quests.py` (NPCs, dialogue, quests, placed fights, parked characters).
