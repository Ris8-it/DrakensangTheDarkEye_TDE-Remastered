SELECT 'new item templates (expect 6): ' || ((SELECT count(*) FROM _Template_Item WHERE Id IN ('arm_q_sigil','arm_q_ledger','arm_q_page1','arm_q_page2','arm_q_page3','arm_q_page4')));
SELECT 'new status effects (expect 0): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN (NULL));
SELECT 'loot entries (expect 0): ' || (0);
SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;
