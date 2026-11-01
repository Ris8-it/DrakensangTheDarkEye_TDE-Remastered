BEGIN;
DELETE FROM _Locale WHERE LocaId IN ('z_arcanethief_N','z_arcanethief_D');
INSERT INTO _Locale ("LocaId","LocaText") VALUES ('MI_TA_M_Info','The pickpocket is proud of his Phex-pleasing handiwork. He is agile and skillful, relieving richer citizens of their heavy purses. He knows his way around the city and is skilled at setting traps, helping him to shake off pursuers and avoid ending up in a prison cell. His preferred weapon is the dagger.');
INSERT INTO _Locale ("LocaId","LocaText") VALUES ('MI_TA_W_Info','The pickpocket is proud of her Phex-pleasing handiwork. She is agile and skillful, relieving richer citizens of their heavy purses. She knows her way around the city and is skilled at setting traps, helping her to shake off pursuers and avoid ending up in a prison cell. Her preferred weapon is the dagger.');
COMMIT;
