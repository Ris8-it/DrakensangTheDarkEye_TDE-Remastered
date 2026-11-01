SELECT 'texts (expect 0): ' || (SELECT count(*) FROM _Locale WHERE LocaId IN ());
SELECT 'locale.db4 integrity check:'; PRAGMA integrity_check;
