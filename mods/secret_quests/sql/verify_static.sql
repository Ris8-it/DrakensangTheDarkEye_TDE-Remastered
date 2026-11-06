SELECT 'new item templates (expect 11): ' || ((SELECT count(*) FROM _Template_Item WHERE Id IN ('arm_q_sigil','arm_q_ledger','arm_q_page1','arm_q_page2','arm_q_page3','arm_q_page4','arm_q_wolf_charm','arm_q_tg_strongbox','arm_q_tg_silver','arm_q_tg_ledger','arm_q_tg_crystal')));
SELECT 'new status effects (expect 0): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN (NULL));
SELECT 'loot entries (expect 0): ' || (0);
SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;
