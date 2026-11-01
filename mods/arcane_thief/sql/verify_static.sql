SELECT 'new item templates (expect 0): ' || (0);
SELECT 'new status effects (expect 0): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN (NULL));
SELECT 'loot entries (expect 0): ' || (0);
SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;
