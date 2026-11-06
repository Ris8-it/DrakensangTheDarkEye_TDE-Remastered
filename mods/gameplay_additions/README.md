# Gameplay Additions (based on the mg979 files)

mg979's **Gameplay Additions v2.1b** (mild preset). The pack was built on these files, and mg979 was the one who suggested
doing it this way, so they are included as its first module. Thanks, mg979.

What it changes (generated as the exact difference between the vanilla databases and vanilla + Gameplay Additions):
- class rules: talent and weapon penalties and bonuses per profession (`_Template_Advantages`), two professions
- loot: 84 loot tables reworked
- balance: 1394 NPC and 220 monster templates (and their placed copies), 46 spells, 42 attacks, shields, weapons, armour
- the world: 449 lights and 193 ambience zones
- Ergo's items (Witch Hat and Robe, Shadow Armour, Druid Staff, Elven Spear, Silver Scimitar and others) with their icons,
  the witch hat skin (the two character models `gfxlib/characters/mensch_*.n2`) and the cultist dagger textures
- also in the same baseline: the player's own two pre-pack fixes (the Witch Hat fix and the Ravenwing Saber)

Each changed value is only written where it still holds vanilla's value, so the module is a no-op on a game that already has
Gameplay Additions (any preset) and never undoes what a later module changed. `Install.bat` of the pack installs it first.
Rebuild: `python -I tools/build_gameplay_additions.py <game>/export/db/armory_backup mods/gameplay_additions`.
