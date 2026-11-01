# Drakensang TDE - Remastered

An item, crafting and quest expansion for **Drakensang: The Dark Eye** (2008, Steam v1.03), and the open toolkit it is built
with. Yes, people still play this game. Some of us also mod it.

## For players

**What it adds**
- About 380 new items in five tiers, from small early finds to a handful of mythic artifacts, placed by story chapter so nothing
  overpowered turns up early. Weapons with on-hit effects, armour sets, cursed rings, joke items.
- **Five crafting lines**, one step per chapter, each fed by what you hunt there: hunter's leather (Wolfpack, Moonhowl,
  Skyhunter), tusk-and-claw medium armour, witch-cloth for casters, an arrow ladder, and talismans from beast trophies.
  Skinning gives trophies; tools (knives, sickles, lockpicks) are reusable quick-slot items.
- **Quests:** a travelling trophy collector with legendary hunts, a duelist circle to break, a mad-scientist's codex, a pack of
  moon-mad wolves, a rumour-monger, and some silly secrets. Written to never spoil the main game.
- An **Arcane Thief** hero archetype, armour rebalanced by class (light / medium / heavy) and stage, and an optional
  **Hard Ending** with tougher late bosses.

**Requirements**
- Drakensang: The Dark Eye, Steam version 1.03.
- mg979's *Gameplay Additions* v2.1b installed first (the pack is built on top of it).
- Windows. The installers are plain `.bat` files using the bundled `sqlite3.exe`.

**Install**
1. Close the game. If it isn't in `D:\Steam\steamapps\common\Drakensang`, set its folder once:
   `setx DRAKENSANG "C:\Your\Path\Drakensang"` (then open a new window).
2. Run `mods\Drakensang_TDE_Remastered\Install.bat`. The first run backs up your databases to `export\db\armory_backup`.
3. Start a **new game**. (Existing saves keep their own copy of the world; new monsters, NPCs and shop stock only appear in a new game.)

`Uninstall.bat` restores the backed-up databases. Your saves are never touched by either.
Everything the pack contains, item by item, is in each module's README under `mods/`.

## For modders

The game keeps almost everything in three SQLite databases (`export/db/static.db4`, `locale.db4`, `game.db4`): items, effects,
loot, recipes, NPCs, dialogue, quests, even scripts. This repository is a toolkit for changing them safely:

- **Generators, not hand-written SQL.** `tools/dsa.py` clones the game's own rows as templates and overrides a few columns, so a
  60-column insert is one line. `tools/quests.py` adds NPCs, dialogue trees, journal quests, placed monsters, and characters who
  arrive later in the story.
- **Every install is reversible and repeatable:** deterministic GUIDs, delete-then-insert, generated undo SQL, verify queries.
- **A full offline test:** `python -I tools/build_all.py` rebuilds every module and installs it twice on copies, checks every
  reference, then uninstalls and proves the databases are identical to before.
- **Save tools** for when a save no longer loads (`tools/maint/save_doctor.py`).

Start with [docs/MODDING_GUIDE.md](docs/MODDING_GUIDE.md); the hard-won engine facts are in [docs/ENGINE_REFERENCE.md](docs/ENGINE_REFERENCE.md).

**Setup:** Python 3.10+ with Pillow and NumPy. Then, once: `python -I tools/extract_vanilla_icons.py` (the game's own icons are
not in this repository; this pulls them from your copy).

## Repository layout

```
mods/                      the built modules (sql/, Install.bat, Uninstall.bat, README.md); Drakensang_TDE_Remastered/ runs them all
tools/
  build_all.py             rebuild every module, then run the full test
  build_*.py               one generator per module; dsa.py (mod writer), quests.py (NPCs, dialogue, quests, monsters)
  armory_data*.py          item data, loaded v21 -> v26 (newest last)
  maint/                   validate.py, save_doctor.py, sync_save_world.py, spoiler_scan.py, slim_sources.py
  art/                     icon pipeline: split_sheet.py (sheets of icons), batch_remastered.py (process), gen_icon.sh (Codex)
  research/                read-only scripts used to learn the engine
  extract_vanilla_icons.py, npk.py   read the game's .npk archives
assets/                    icon source art (original), prompts, processed icons, the original icon sheets
docs/                      MODDING_GUIDE, ENGINE_REFERENCE, DESIGN_RULES, CRAFTING_PLAN; history/
```

## Credits and notes

Made by Ris8 over many evenings in autumn 2026. Built on top of mg979's *Gameplay Additions*.
*Drakensang: The Dark Eye* and its assets belong to their owners. Code and new artwork are MIT-licensed (see `LICENSE`). The
repository contains no game files except a few tinted copies of the game's own icons, used as fallbacks for items without new art.
