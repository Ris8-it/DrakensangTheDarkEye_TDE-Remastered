BEGIN;
DELETE FROM _Categories WHERE CategoryName='LayLabShrine';
DROP TABLE IF EXISTS "_Template_LayLabShrine";
COMMIT;
