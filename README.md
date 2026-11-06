# Drakensang TDE - Remastered

An item, crafting and quest mod for *Drakensang: The Dark Eye* (2008, Steam v1.03), based on the mg979 files.
Yes, people still play this game. Some of us also mod it.

It started as a few items on top of mg979's *Gameplay Additions* and kept growing. mg979 was the one who suggested building
on their SQL files, so their mod is included here as the first module (`mods/gameplay_additions`). If you already have it
installed, nothing changes.

The main story is left alone. New items and quests are placed by chapter, and none of the texts spoil what comes later.

## What's in it

From mg979's Gameplay Additions v2.1b:
- class rules for talents and weapons, two reworked professions
- reworked loot tables, rebalanced NPCs, monsters, spells and attacks
- about 450 extra lights and 190 ambience zones
- Ergo's items (Witch Hat and Robe, Shadow Armour, Druid Staff, Elven Spear, Silver Scimitar and a few more)

Items and crafting:
- around 380 new items in five tiers (regular, amazing, super rare, legendary, mythic): weapons with on-hit effects,
  armour sets (dwarven, Kurkum, Nightfox, dragon-scale), 50+ rings and amulets, some cursed, some just jokes
- upgraded Wyrm and Pal'Na'Thar weapons, a bigger dragon hoard, heirloom weapons for Rhulana, Gwendala and Forgrimm
- five crafting lines, one step per chapter: hunter's leather (Wolfpack, Moonhowl, Skyhunter), tusk-and-claw medium
  armour, witch-cloth for casters, an arrow ladder, and talismans
- skinning gives trophies (fangs, claws, tusks) for the talismans
- weapon oils, traps, wands, scrolls, and four weapons that roll a skill check on hit
- easier crafting; knives, sickles and lockpicks are reusable quick-slot tools

Quests (none of them announced, Wendelin the rumour-monger in Ferdok hints at all of them):
- Teeth for the Collector: Ulfried Pelzfeld, a trophy hunter you meet in Avestrue and again later, wants legendary beasts
- The Crimson Circle: seven duelists hidden from Ferdok harbour to the Fire Falls, with rivals for Rhulana, Gwendala
  and Forgrimm
- The Codex of Hidden Fire: Rakorium's missing pages
- The Mad Pack and The Moon-Thread: moon-mad wolves in the Dark Forest lead to a silver thread, Auralia, the leprechaun
  and a pelt collector, and end with a fight at the witches' dancing place and a choice between two rewards
- the Thieves' Guild and a few small things along the way

Other:
- Arcane Thief: the Thief can learn battle-mage spells
- armour rebalanced by class (light, medium, heavy) and chapter
- Hard Ending (optional): tougher late enemies and bosses
- World Systems (optional, beta): shrines with party blessings, herb patches that regrow, hunting grounds that refill,
  elites that rally, wolves that howl for the pack, ogres that slam the ground
- Smarter Foes (optional, beta): better target choice, bandits run when badly hurt
- Unofficial Patch (optional): vanilla data fixes (big wolves, emerald spiders and troll toads that dropped nothing because
  of misspelled loot tables, skeleton archers without loot, missing descriptions)

The optional ones each have an `Install_*.bat` in `mods/Drakensang_TDE_Remastered/`. The full lists (every item, effect and
location) are in each module's README under `mods/`.

## Install

Needs Drakensang: The Dark Eye, Steam version 1.03, on Windows. That's it, mg979's files are included.

1. Close the game. If it isn't in `D:\Steam\steamapps\common\Drakensang`, set its folder once:
   `setx DRAKENSANG "C:\Your\Path\Drakensang"` (then open a new window).
2. Run `mods\Drakensang_TDE_Remastered\Install.bat`. The first run backs up your databases to `export\db\armory_backup`.
3. Start a **new game**. Existing saves keep their own copy of the world, so new monsters, NPCs and shop stock only
   appear in a new game.

`Uninstall.bat` restores the backed-up databases. Neither script touches your saves.

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

- **Engine layers:** [docs/ENGINE_ARCHITECTURE.md](docs/ENGINE_ARCHITECTURE.md) maps how the engine works and where new systems can be
  hooked in through data; `tools/layers.py` generates each of those layers (AI state machines, presets, triggers, encounters, level
  scripts, factions, ...), `tools/engine/` decodes the game's scripts and machines, `mods/engine_lab` is the in-game test pack.

Start with [docs/MODDING_GUIDE.md](docs/MODDING_GUIDE.md); the hard-won engine facts are in [docs/ENGINE_REFERENCE.md](docs/ENGINE_REFERENCE.md).

**Setup:** Python 3.10+ with Pillow and NumPy. Then, once: `python -I tools/extract_vanilla_icons.py` (the game's own icons are
not in this repository; this pulls them from your copy).

## Repository layout

```
mods/                      the built modules (sql/, Install.bat, Uninstall.bat, README.md); Drakensang_TDE_Remastered/ runs them all
tools/
  build_all.py             rebuild every module, then run the full test
  build_*.py               one generator per module; dsa.py (mod writer), quests.py (NPCs, dialogue, quests, monsters),
                           layers.py (the 18 engine layers), loosefiles.py (patched data/tables/*.xml from your own archives)
  engine/                  read-only decoders: dsa_script.py (scripts, AI machines, quests), vocab.py, engine_map.py, xltable.py, save_diff.py
  armory_data*.py          item data, loaded v21 -> v26 (newest last)
  maint/                   validate.py, sqlrun.py, save_doctor.py, sync_save_world.py, spoiler_scan.py, slim_sources.py
  art/                     icon pipeline: split_sheet.py (sheets of icons), batch_remastered.py (process), gen_icon.sh (Codex)
  research/                read-only scripts used to learn the engine
  extract_vanilla_icons.py, npk.py   read the game's .npk archives
assets/                    icon source art (original), prompts, processed icons, the original icon sheets
docs/                      MODDING_GUIDE, ENGINE_REFERENCE, ENGINE_ARCHITECTURE, DESIGN_RULES, CRAFTING_PLAN; history/
```

## Credits and notes

Made by Ris8 over many evenings in autumn 2026. Based on the mg979 files: *Gameplay Additions* v2.1b by mg979, included with
thanks.
*Drakensang: The Dark Eye* and its assets belong to their owners. Code and new artwork are MIT-licensed (see `LICENSE`). The
repository contains no game files except a few tinted copies of the game's own icons (fallbacks for items without new art) and
mg979's files in `mods/gameplay_additions/loose` (their icons and textures, and the two character models edited for the witch hat).
