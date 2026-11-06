SELECT 'texts (expect 1): ' || (SELECT count(*) FROM _Locale WHERE LocaId IN ('lookat_lab_shrine'));
SELECT 'locale.db4 integrity check:'; PRAGMA integrity_check;
