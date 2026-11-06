# Unofficial Patch (optional)

Fixes for broken references in the vanilla data (missing loot, misspelled script names, missing texts).
Found by the research database atlas (dangling references with a nearest existing key) and checked one by one.
Every change is guarded and undone exactly by Uninstall.bat.

| Fix | What | Affects |
|---|---|---|
| Loot | `loot_wolf_groß` (copy of `loot_wolf_großo`) | 3 templates: Wolf_loc03_alwene, Wolf_02_loc03_alwene, Wolf_03_loc03_alwene |
| Loot | `loot_smaragdspinne_groß` (copy of `loot_smaragdspinne_groß?`) | 8 templates: Smaragdspinne, Smaragdspinne_loc00z4, Smaragdspinne_loc05, Smaragdspinne_loc02, Smaragdspinne_loc08, Smaragdspinne_loc10 ... |
| Loot | `loot_trollkroete_groß` (copy of `loot_trollkroete_groß?`) | 6 templates: Trollkroete_loc03_hexen, Trollkroete_02_loc03_hexen, Allwiss, Trollkroete_03_loc03_hexen, loc04_trollkroete, Trollkroete_loc09 |
| Loot | `loot_skelett_leicht_fern` (copy of `loot_skelett_leicht_fern_bogen`) | 3 templates: Skelett_leicht, dun08_gruft_skelett_fernkampf, Skelett_leicht_loc04_fern |
| Preset | `preset_on_hurt_swap_target.xml` = alias of `preset_on_hit_swap_target.xml` | Smaragdspinne_klein_loc05_orkkampf |
| Idle routine | `loc03_ba_berndrich_wache.xml` → `lo03_ba_berndrich_wache.xml` | template praiot_klein_loc03_fern_teich |
| Idle routine | `loc03_ba_berndrich_wache.xml` → `lo03_ba_berndrich_wache.xml` | placed NPC Loc03PraiotKroete03 |
| Idle routine | `loc08_ba_tallon_belebung_friedhof_runde_02xml` → `loc08_ba_tallon_belebung_friedhof_runde_02.xml` | template loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02 |
| Texts | 11 missing description texts | 9 chests, 2 orcish war dogs |

Loot, preset and texts are static data: they work on existing saves (monsters already placed in a save keep their
own LootTable name, which is the same broken name, so they also drop loot now). The guard's idle routine is a placed
instance: new game, or SyncSave.bat.

Not changed (needs an in-game test first): Behaviour `basic_monster` on three cave troll toads (the machine does not
exist; what the game does with it is unknown), and sound cues whose names differ from the sound objects.
