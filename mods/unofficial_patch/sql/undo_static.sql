BEGIN;
UPDATE "_Template_NPC" SET "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02xml' WHERE "Id"='loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02' AND "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02.xml';
UPDATE "_Template_NPC" SET "BaseActionScript"='loc03_ba_berndrich_wache.xml' WHERE "Id"='praiot_klein_loc03_fern_teich' AND "BaseActionScript"='lo03_ba_berndrich_wache.xml';
DELETE FROM _DSA_Preset WHERE PresetName='preset_on_hurt_swap_target.xml';
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_skelett_leicht_fern';
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_trollkroete_groﬂ';
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_smaragdspinne_groﬂ';
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_wolf_groﬂ';
COMMIT;
