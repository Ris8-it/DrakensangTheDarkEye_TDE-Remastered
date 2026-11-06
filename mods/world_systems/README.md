# World Systems (optional)

New play built on the engine layers (`tools/layers.py`, `docs/ENGINE_ARCHITECTURE.md`). Install after the pack; uninstall restores
exactly what it changed (every edit of a vanilla row is guarded: if another mod changed that row first, it is left alone).

**New game recommended.** Shrines, herb patches, hunting grounds and placed wolves/ogres live in the world database; on an existing
save only the static parts work (rally/frenzy, ground slam, howling for wolves spawned later) unless the save is synced with
`tools/maint/sync_save_world.py`.

| Feature | What | Where | Effect |
|---|---|---|---|
| Shrine | Shrine of Phex | location02_praios | Haggle +2, Pick Locks +1, Pick Pocket +1 for 15 min (whole party); early |
| Shrine | Shrine of Firun | location03 | Survival +2, Animal Lore +2, Bow +1 for 15 min (whole party); mid |
| Shrine | Shrine of Peraine | location04 | Treat Wounds +2, Treat Poisons +2, Plant Lore +2 for 15 min (whole party); mid |
| Shrine | Shrine of Rondra | location08 | Attack +1, Parry +1, Courage +1 for 15 min (whole party); late |
| Shrine | Shrine of Ingerimm | location09 | Strength +1, Constitution +1, Blacksmith +2 for 15 min (whole party); endgame |
| Herb patch | kraut_belmart | location03 | regrows every 3rd visit |
| Herb patch | kraut_chonchinis | location03 | regrows every 3rd visit |
| Herb patch | kraut_einbeere | location03 | regrows every 3rd visit |
| Hunting ground | Baer, Wolf, Wolf_02 | location03 | from the 2nd visit; every 20 min, 4 times |
| Herb patch | kraut_alraune | location04 | regrows every 3rd visit |
| Herb patch | kraut_belmart | location04 | regrows every 3rd visit |
| Herb patch | kraut_einbeere | location04 | regrows every 3rd visit |
| Herb patch | kraut_belmart | location05 | regrows every 3rd visit |
| Herb patch | kraut_chonchinis | location05 | regrows every 3rd visit |
| Herb patch | kraut_einbeere | location05 | regrows every 3rd visit |
| Herb patch | kraut_belmart | location08 | regrows every 3rd visit |
| Herb patch | kraut_chonchinis | location08 | regrows every 3rd visit |
| Herb patch | kraut_efeuer | location08 | regrows every 3rd visit |
| Hunting ground | Baer02, Wildschwein, Wolf_03 | location08 | from the 2nd visit; every 20 min, 4 times |
| Herb patch | kraut_eitriger_kroeten | location10 | regrows every 3rd visit |
| Herb patch | kraut_feuermoos | location10 | regrows every 3rd visit |
| Herb patch | kraut_eitriger_kroeten | location10 | regrows every 3rd visit |
| Last Stand | 10 elite fighters | everywhere but the final mountain | below 1/3 LE: AT +2 PA +2 for 30 s, once |
| Frenzy | 46 large beasts | everywhere but the final mountain | below 1/4 LE: AT +3 PA -2 for 30 s, once |
| Wolf pack | 15 wolf kinds | everywhere | howl (calls the pack), then attack the nearest; machine monster_wolf |
| Ground Slam | 14 ogre kinds | Tallon and later | 1 in ~8 attacks: KK+4 check or knocked down, 1d6+2 to the party within 4 m |

## Status: needs an in-game test

Built from vanilla patterns, checked offline (`python -I tools/maint/validate.py --mods world_systems`). Not yet seen in play:

1. Shrine placement (2.5 m from the workbench; move with the offsets in `build_world_systems.py` if one stands in a wall).
2. `can:Use` on an Object (vanilla uses it on items and workbenches).
3. Regrowth timing (vanilla runs its player-house regrowth the same way).
4. `ActingEntity` inside a ScriptCombatAction script (the ground slam). If nothing happens, see engine_lab probe P5.
5. The revived wolf howl (animation `Idle_Howl`).
