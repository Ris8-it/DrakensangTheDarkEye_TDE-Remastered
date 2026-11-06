BEGIN;
-- loot table loot_wolf_groﬂ (copy of the misnamed or nearest vanilla table)
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_wolf_groﬂ';
INSERT INTO _DSA_LootTables ("LootTableName","LootTableValue","LootTableContent") VALUES ('loot_wolf_groﬂ','1','Item/Fellfetzen/100/w2/2/;Item/generic_wolfskralle/80/w2/4/;');
-- loot table loot_smaragdspinne_groﬂ (copy of the misnamed or nearest vanilla table)
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_smaragdspinne_groﬂ';
INSERT INTO _DSA_LootTables ("LootTableName","LootTableValue","LootTableContent") VALUES ('loot_smaragdspinne_groﬂ','1','Item/spinnenfangzaehne/100/w2/200/;Item/seidendruese/100/1/16/;');
-- loot table loot_trollkroete_groﬂ (copy of the misnamed or nearest vanilla table)
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_trollkroete_groﬂ';
INSERT INTO _DSA_LootTables ("LootTableName","LootTableValue","LootTableContent") VALUES ('loot_trollkroete_groﬂ','0','Item/froschschenkel/100/w2/6/;');
-- loot table loot_skelett_leicht_fern (copy of the misnamed or nearest vanilla table)
DELETE FROM _DSA_LootTables WHERE LootTableName='loot_skelett_leicht_fern';
INSERT INTO _DSA_LootTables ("LootTableName","LootTableValue","LootTableContent") VALUES ('loot_skelett_leicht_fern','1','Weapon/Kurzbogen/50/1/150/;Ammo/Pfeil/100/w20+20/1/;');
-- preset preset_on_hurt_swap_target.xml (based on preset_on_hit_swap_target.xml)
DELETE FROM _DSA_Preset WHERE PresetName='preset_on_hurt_swap_target.xml';
INSERT INTO _DSA_Preset ("PresetName","PresetType","PresetActionName","PresetScriptName") VALUES ('preset_on_hurt_swap_target.xml','OnAction','DamageTaken','loc05_on_hit_swap_target.xml');
UPDATE "_Template_NPC" SET "BaseActionScript"='lo03_ba_berndrich_wache.xml' WHERE "Id"='praiot_klein_loc03_fern_teich' AND "BaseActionScript"='loc03_ba_berndrich_wache.xml';
UPDATE "_Template_NPC" SET "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02.xml' WHERE "Id"='loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02' AND "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02xml';
COMMIT;
