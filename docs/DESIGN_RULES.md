# Design rules

Every rule the player has set for the pack, in one place. They override anything older in `docs/history/` or `docs/reviews/`.
When a request changes a rule, change it here in the same session.

## 1. Where the game happens (stages)

| Stage | Levels | Story |
|---|---|---|
| tutorial | `location01` Avestrue, `dungeon01_*` | before Ferdok; the real game starts in Ferdok |
| early | `location02_*` Ferdok, `dungeon02_*` | chapter 1. The Count's Town (`location02_grafenstadt`) opens later than the rest of Ferdok |
| mid | `location03` Dark Forest / Blood Mountains, `location04` Moorbridge, `location05` + `dungeon05_burg` Silver Falls and Castle Grimmzahn | chapters 2-3 |
| late | `location08*` Tallon, `dungeon08_*` | chapter 4 |
| endgame | `location09` Murolosh, `location10` Deeps of Gruldur, `location11` Fire Falls | chapters 5-6 |
| never | `location12` Drakensang Mountain | final, one-way: place nothing there |

Monsters that appear late: scorpions only in the Murolosh mushroom garden (after Tallon); harpies and tatzelwurms from Tallon;
crypt lice from the Moorbridge crypts; emerald spiders under the Ferdok oracle (optional) and late caves.

## 2. No spoilers

- Quest titles, objectives, journal riddles, rumours and early dialogue stay vague: never the name or exact place of a later
  location, boss or monster kind. "Something lives beneath the place where people go to ask about the future", not "the oracle spider".
- A text may be explicit only where the player already is or already holds the thing: a trophy's own description, a line said
  in that place, a close-of-quest entry, endgame dialogue.
- Plans and item texts sold early must not name later monsters (that is why the spider trophy is "Glittering Green Eye").
- Check with `python -I tools/maint/validate.py --spoilers`.

## 3. Items and power

- Strong items come late. Too-good early finds get moved (Gambler's Die: Tallon lair corpse; Whisper of Phex: Grimmzahn; Hammer
  of Mild Annoyance: the smugglers' stash behind the sewer wall, not on Jischka).
- Early items: talents and small bonuses only, no attributes and no regeneration.
- Mythic only from dungeons or one-off reforges, never shop stock, never mass-craftable.
- No unique items in pickpocket tables.
- Casters wear no metal. Forgrimm is a two-handed fighter. Rhulana uses sabres.
- Never use elven/buckskin boot skins (`schuhe_elfen`, `schuhe_gwendala`, `schuhe_lederstiefel_04/05/06`); prefer `schuhe_nasreddin`.
- Tools (skinning knives, sickles, lockpicks) are quick-slot items with `UseTalent` + `TaBonus` on a `CanDestroy 0` base:
  reusable, never equippable weapons, no duplicates in a shop.
- Joke items stay jokes (Cano's Signet: Etiquette up, Haggle down). Don't make a second thief ring.
- Economy: about 1000 ducats per playthrough. Keep sell values low (merchants pay 50 %).
- Tooltips compact; lore and balance notes belong in docs.

## 4. Armour (applied automatically by `armory_data_v26.py` / `armour_rules`)

Class by material: **Cloth** = light (casters), **Leather** = medium-light, **Metal** = heavy. Each pack piece is clamped to the
most total protection (sum of the 8 zones) its slot and class may have at its stage, and gets at least the encumbrance vanilla
gives per point of protection. Stage = where it is first found or sold (else its tier). The build prints every adjustment.

| Slot | Cloth | Leather | Metal | BE per point (leather / metal) |
|---|---|---|---|---|
| chest | 7 / 9 / 12 / 14 | 14 / 17 / 20 / 23 | 18 / 22 / 26 / 30 | 0.10 / 0.16 |
| head | 2 / 3 / 3 / 4 | 4 / 5 / 6 / 6 | 5 / 6 / 6 / 7 | 0.10 / 0.15 |
| shoulders | 3 / 4 / 5 / 6 | 6 / 8 / 10 / 12 | 8 / 10 / 12 / 14 | 0.025 / 0.05 |
| arms | - | 6 / 8 / 10 / 10 | 8 / 10 / 12 / 12 | 0.03 / 0.04 |
| gloves | 2 / 3 / 4 / 4 | 4 / 6 / 6 / 8 | 6 / 8 / 10 / 10 | 0 / 0.03 |
| legs, boots, trousers | 3 / 4 / 5 / 6 | 7 / 9 / 10 / 12 | 8 / 10 / 12 / 14 | 0 / 0.06 |

(caps for early / mid / late / endgame). Fur pieces of the hunter line: all non-chest pieces together at most 1.0 encumbrance.

## 5. Crafting: five lines, one step per chapter

Each step needs something hunted or looted in that area; plans are sold where that material first appears; a plan never names
something the player has not met. Beast parts drop more easily in later areas.

| Line | Skill | Avestrue/Ferdok | Ch 2 (Dark Forest, Moorbridge) | Tallon | Murolosh and later |
|---|---|---|---|---|---|
| Hunter's leather | Bowcraft | Wolfpack (Crooked Otto) | Moonhowl (Hagen, after the mad pack) | Skyhunter (Tallon hunter) | Wyrmhide |
| Tusk and claw | Smithing / Bowcraft | Tuskhide (Count's Town smith, Otto) | Ironshell (Moorbridge smith) | Warlord (Tallon crafts) | dwarven steel, wyrm scale |
| Smith metals | Smithing | steel | Kosh steel | Kosh steel | dwarven steel, wyrm scale |
| Witch-cloth | Alchemy | - | Witchweave (Saphira) | Emberweave (Tallon magic trainer) | Dragonblood Robe |
| Arrows | Bowcraft | Barbed, Kosch Hunter's | Moon-sinew (Dark Forest trader) | Hawk, Sleepthorn, Thunder, Frost | Dwarven bolts, Wyrmfang |
| Talismans | Bowcraft | wolf, boar, rat; Warding Charm I | Warding Charm II (Moorbridge druid) | Warding III, ember, tatzelwurm | scorpion, wyrm horn |

All wolf plans are sold only by Crooked Otto (Count's Town). Older plans swap one gemstone/gold leaf for the local beast part
(`BEAST_SWAP` in `armory_data_v26.py`). Upgrades consume the previous piece and say so in the plan.

## 6. Quests

- Ulfried, Wendelin, Klingenhand, Rakorium's codex and Hagen follow §2.
- The Crimson Circle starts only after Moorbridge: Klingenhand waits outside the Golden Lance (the tavern itself opens only with
  Rhulana's quest) and the duelists are parked until he gives the job.
- Hard fights are welcome where the story allows (the mad pack: 15 wolves, chapter 2).
- Unique beasts and bosses are wound-immune, have high magic resistance (willpower), +1-2 armour and a life pool matching their
  story weight (`tools/beasts_data.py`; the pack's own legends +30 % life). Hard Ending scales on top of these values.

## 7. Abilities

- Light-fighter and thrower abilities ask for the attributes those builds have (Courage low, no Strength for throws); the
  old class mod's walls are lowered in `build_remastered.py` (ABILITIES). Tooltip "Requires:" lines are generated, never typed.

## 8. Icons

- Painted, slightly desaturated, warm light from the upper left, soft dark shadow; judged at 128 px on parchment.
- Tier glow added by the pipeline (blue amazing, violet superrare, gold legendary, subtle red mythic); sheets are split and re-glowed.
- Long objects diagonal from lower left to upper right.
