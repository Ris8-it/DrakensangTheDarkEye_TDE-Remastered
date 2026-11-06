SELECT 'new item templates (expect 15): ' || ((SELECT count(*) FROM _Template_Armor WHERE Id IN ('arm_mt_mantle')) + (SELECT count(*) FROM _Template_Item WHERE Id IN ('arm_q_sigil','arm_q_ledger','arm_q_page1','arm_q_page2','arm_q_page3','arm_q_page4','arm_q_wolf_charm','arm_q_moon_knot','arm_q_moon_bill','arm_q_tg_strongbox','arm_q_tg_silver','arm_q_tg_ledger','arm_q_tg_crystal')) + (SELECT count(*) FROM _Template_Jewelry WHERE Id IN ('arm_mt_tear')));
SELECT 'new status effects (expect 2): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN ('PeArmMoontear','PeArmMoonmantle'));
SELECT 'loot entries (expect 0): ' || (0);
SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;
