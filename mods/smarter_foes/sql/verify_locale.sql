SELECT 'texts (expect 3): ' || (SELECT count(*) FROM _Locale WHERE LocaId IN ('LayFled_name','LayFled_short','LayFled_long'));
SELECT 'locale.db4 integrity check:'; PRAGMA integrity_check;
