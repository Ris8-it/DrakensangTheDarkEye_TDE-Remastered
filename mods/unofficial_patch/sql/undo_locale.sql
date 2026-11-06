BEGIN;
DELETE FROM _Locale WHERE LocaId IN ('infoid_loc02_spielerhaus_werkbank_kiste','infoid_loc02_spielerhaus_werkbank_truhe','infoid_loc03_truhe_da_vanya','infoid_loc03_truhe_ronkwer','infoid_loc03_truhe_humpert','infoid_loc03_truhe_saphira','infoid_loc03_truhe_guthof','infoid_loc03_truhe_koch','infoid_loc03_truhe_danor','infoid_Kampfhund_loc05_orks_innen_pat1','infoid_Kampfhund_loc05_orks_innen_pat2');
COMMIT;
