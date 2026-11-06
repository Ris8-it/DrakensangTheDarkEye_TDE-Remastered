SELECT 'new item templates (expect 0): ' || (0);
SELECT 'new status effects (expect 0): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN (NULL));
SELECT 'loot entries (expect 0): ' || (0);
SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;
SELECT 'loot table loot_skelett_leicht_fern (expect 1): ' || (SELECT count(*) FROM _DSA_LootTables WHERE LootTableName='loot_skelett_leicht_fern');
SELECT 'preset preset_on_hurt_swap_target.xml rows (expect 1): ' || (SELECT count(*) FROM _DSA_Preset WHERE PresetName='preset_on_hurt_swap_target.xml');
SELECT '_Template_NPC.BaseActionScript of praiot_klein_loc03_fern_teich (expect 1): ' || (SELECT count(*) FROM "_Template_NPC" WHERE "Id"='praiot_klein_loc03_fern_teich' AND "BaseActionScript"='lo03_ba_berndrich_wache.xml');
SELECT '_Template_NPC.BaseActionScript of loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02 (expect 1): ' || (SELECT count(*) FROM "_Template_NPC" WHERE "Id"='loc08_tallon_stadtbelebung_weiblich_friedhof_roaming_02' AND "BaseActionScript"='loc08_ba_tallon_belebung_friedhof_runde_02.xml');
