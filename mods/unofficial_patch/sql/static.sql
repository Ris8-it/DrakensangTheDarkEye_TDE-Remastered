BEGIN;
-- loot table loot_skelett_leicht_fern (copy of the misnamed or nearest vanilla table)
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_skelett_leicht_fern';
INSERT INTO _DSA_LootTables ("LootTableName","LootTableValue","LootTableContent") VALUES ('loot_skelett_leicht_fern','1','Weapon/Kurzbogen/50/1/150/;Ammo/Pfeil/100/w20+20/1/;');
-- preset preset_on_hurt_swap_target.xml (based on preset_on_hit_swap_target.xml)
DELETE FROM _DSA_Preset WHERE PresetName='preset_on_hurt_swap_target.xml';
INSERT INTO _DSA_Preset ("PresetName","PresetType","PresetActionName","PresetScriptName") VALUES ('preset_on_hurt_swap_target.xml','OnAction','DamageTaken','loc05_on_hit_swap_target.xml');
UPDATE "_Template_NPC" SET "BaseActionScript"='lo03_ba_berndrich_wache.xml' WHERE "Id"='praiot_klein_loc03_fern_teich' AND "BaseActionScript"='loc03_ba_berndrich_wache.xml';
UPDATE "_Template_NPC" SET "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02.xml' WHERE "Id"='loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02' AND "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02xml';
COMMIT;
