SELECT 'texts (expect 2): ' || (SELECT count(*) FROM _Locale WHERE LocaId IN ('z_arcanethief_N','z_arcanethief_D'));
SELECT 'locale.db4 integrity check:'; PRAGMA integrity_check;
