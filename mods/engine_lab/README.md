# Engine Lab (test pack, not for normal play)

Install on a test copy of the game, start a NEW game. Rhulana carries the numbered Lab items (reusable). Use each, note what you see.
"Risky" probes test words the vanilla game never uses: an engine assertion is a valid answer (= not supported). **Save before each.**
Afterwards: Uninstall.bat (and LooseFiles_Uninstall.bat). Stage 2 (`mods/engine_lab_stage2`) only after P12 passed.

| Probe | Layer | Do | Expect | Answers | Risky |
|---|---|---|---|---|---|
| P01 IsEquipped | layer 13 (unused designer atom) | Use with Rhulana's starting weapon equipped, then unequipped. | Two different messages: "equipped: yes/no". An assert = the atom does not exist. | Does IsEquipped exist (fills the "no is-equipped atom" gap)? | yes |
| P02 IsItemAddable | layer 13 | Use once. | "addable: yes/no". An assert = missing atom. | Does IsItemAddable exist? | yes |
| P03 IsDialogUnLocked | layer 13 | Use once. | "unlocked: yes/no". | Does IsDialogUnLocked exist? | yes |
| P04 IsSubTaskUnLocked | layer 13 | Use once. | "subtask: yes/no". | Do the IsSubTask* atoms exist? | yes |
| P05 AddItem | layer 13 (unused designer verb) | Use once, open the inventory. | A "Lab Coin" appears. | Does AddItem exist? | yes |
| P06 ActingEntity radius script | layers 5/8 | Stand next to Rhulana and Dranor, use. | Every hero within 6 m says "inside the radius". | Does RunActionScriptInRadius who="ActingEntity" work (the ogre Ground Slam relies on it)? |  |
| P07 Custom attribute | layer 18 (new column) | Use 3 times, save, then inspect the save with tools/engine/save_diff.py or sqlite. | _Instance_PC.LayLabValue of the hero = 3. | Does ModifyAttribute accept an attribute declared only in _Attributes + a new column? | yes |
| P08 Hero scripted maneuver | layer 5 | Open Rhulana's special attacks (she knows SF_LayLabStrike), use "Lab Strike" on an enemy. | The maneuver is listed; using it shows "scripted maneuver ran" and hits for 1d6+1. | Can heroes learn/use a Game::ScriptCombatAction? |  |
| P09 Heartbeat | layer 9 | Use once with Rhulana in the party, once without. | "pulse" 6 times, 5 s apart; with Rhulana also her line (If inside a status block, with the automatic Else). | Do unrolled status-effect loops with If/Else run? |  |
| P10 Lab faction | layer 15 | Use: a rat of the new faction FaLayLab appears next to the hero. | It attacks (FaLayLab is hostile to the player). P20 uses it too. | Does a faction added as a new column work? | yes |
| P11 Area hazard | layer 16 | Use: a cloud appears at the hero. | Heroes inside say "hazard tick" (InsideActions of a new AreaSpellTrigger). | Can scripts create AreaSpellTrigger entities with their own scripts? | yes |
| P12 Loose effects.xml | layer 14 | First run LooseFiles_Install.bat, restart the game, use. | A Balsam glow at the hero (effect alias LayLabGlow). | Do loose data/tables/*.xml files override the archives? | yes |
| P13 Zone | layer 8 | Use inside the triangle of lab markers right at the start, then far away. | "in zone" vs "outside". | Does IsInside with MarkerPoint edges work for scripts? |  |
| P14 LockTask | layer 13 | Use once; open the journal. | Message; the lab task (P14) shows as locked or nothing changes. | Do LockTask/LockQuest exist? | yes |
| P15 Watcher | layer 9 | Use P15, then P05 (AddItem) or drop/pick up a Lab Coin. | "watcher fired" once the coin is in the inventory. | Does WaitForCondition wait for a condition script? |  |
| P16 Altar gate | layers 2/10 | Use the Lab Altar next to the start (3 m). Then use P09 (40 s mark) and try the altar again. | First "altar used"; during the pulse mark the altar cannot be used. | Do on:Use and can:Use work on an Object? |  |
| P17 Level enter | layer 6 | Leave Avestrue (any exit) and come back twice. | "level-enter script ran" on every entry, plus "not the first" from the 2nd. | Does a mod-added LevelEnterScript run on every entry? |  |
| P18 Trigger | layer 7 | Walk onto the Lab Altar and away again. | "trigger entered"/"trigger left" every time. | Do new trigger volumes fire (and re-fire)? |  |
| P19 Blueprint patch | layer 17 | After LooseFiles_Install.bat: reach a large monster (Tallon). | Large monsters show a health bar. | Does a loose blueprints.xml load? |  |
| P20 DamageTaken tokens | layer 1 | Use P10, hit the lab rat. | The rat says "AimedEntity", the attacker says "ActingEntity"; on death "on:Death ran". | Which token is the victim in an on:DamageTaken script? |  |
| P21 Kräuter (cp1252) | text encoding | Look at this item and P21b in the inventory and in the tooltip. | Whichever of the two shows "Kräuter" correctly is the encoding to use for all mod text. | cp1252 or UTF-8 for non-ASCII mod text? |  |

## Stage 2: new category

After P12 passed (loose files load) and with LooseFiles_Install.bat applied: install `engine_lab_stage2`, start a new
game. A second altar ("Lab Shrine (new category)") stands 3 m on the other side of the start. If Avestrue loads and it can be used,
layer 18 works: new entity categories are possible from data. If the level aborts, uninstall stage 2.

## Report back

For each probe: pass / fail / assert text. Results go into docs/ENGINE_REFERENCE.md §9 like the Phase 0 results.
