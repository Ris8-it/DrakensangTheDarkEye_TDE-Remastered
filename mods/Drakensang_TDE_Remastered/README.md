# Drakensang TDE - Remastered

A full item and gameplay expansion for **Drakensang: The Dark Eye** (Steam v1.03). Based on the mg979 files ("Gameplay Additions" v2.1b, included as the first module).
Close the game, run `Install.bat`, then start a **new game**. Everything is reversible with `Uninstall.bat`.

## What's inside

| Module | Folder | What it adds |
|---|---|---|
| Gameplay Additions (based on the mg979 files) | `../gameplay_additions` | mg979's v2.1b (mild preset): class-specific talent and weapon rules, reworked loot, monster and NPC balance, spells and attacks, 449 lights and 193 ambience zones, Ergo's items. Installed first; a no-op where it is already installed |
| Armory | `../armory_v2` | 163 tiered items (regular, amazing, super rare, legendary, mythic): weapons with on-hit procs and combos, armour sets (dwarven, Kurkum, Nightfox, dragon-scale), 50+ jewelry pieces incl. cursed rings, 36 upgrade recipes, upgraded Wyrm and Pal'Na'Thar weapons, arrow ladder, dragon-hoard materials |
| Arcane Thief | `../arcane_thief` | The Thief class becomes a dagger/throwing hybrid caster (learns battle-mage spells, AE 22, MR +2) |
| Systems | `../remastered_systems` | Trophies from skinning (Animal Lore), 12 trophy talismans, 6 weapon oils, 6 new traps, 4 wands, 5 scrolls, 4 skill-check weapons, living-weapon upgrade chains, 4 set bonuses |
| Quests | `../quest_avestrue` | Ulfried Pelzfeld, trophy collector next to Owlstone in Avestrue: quest "Teeth for the Collector" and a furrier's shop |
| Secret quests | `../secret_quests` | The Crimson Circle (seven duelists with legendary gear, from Ferdok harbour to the Fire Falls; Rhulana, Gwendala and Forgrimm rivals), Rakorium's Codex of Hidden Fire, the Mad Pack and The Moon-Thread (Dark Forest to Tallon), the Thieves' Guild, and Wendelin the rumour-monger who hints at every secret |
| Hard Ending (optional) | `../hard_ending` | Tougher late enemies and bosses (`Install_HardEnding.bat`) |

Each module folder has its own README with every item, effect and location.

## Design rules
- Gold stays scarce: most power is found in dungeons, boss loot or crafted; shops sell the basics, recipes and tools.
- Nothing unique hides in pickpocket tables; nothing is placed on Drakensang Mountain (one-way final area).
- Ordinary gear stays useful: it is the base for upgrade recipes and can be bought again.
- Item tooltips use native-style effect lines; long explanations live in these READMEs.
- Crafting is eased (recipe difficulty -2, artisan rings and native tools in early shops).

## Install order (done by Install.bat)
1. Restores the clean databases saved before the pack was first installed (`export/db/armory_backup`), so nothing from an older version of the pack is left behind. The databases it replaces are kept in `export/db/before_reinstall`. On the very first install it saves your databases there (and removes Armory v1 if present).
2. gameplay_additions, armory_v2, arcane_thief, remastered_systems, quest_avestrue, secret_quests.
3. Hard Ending again, if it was installed. Otherwise optional: Install_HardEnding.bat.

`Uninstall.bat` restores the same clean databases. Saves are never touched by either.
