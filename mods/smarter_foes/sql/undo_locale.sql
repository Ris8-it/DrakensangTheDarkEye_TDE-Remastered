BEGIN;
DELETE FROM _Locale WHERE LocaId IN ('LayFled_name','LayFled_short','LayFled_long');
COMMIT;
