BEGIN;
DROP TABLE IF EXISTS "_Instance_LayLabShrine";
CREATE TABLE '_Instance_LayLabShrine' ( "Guid" BLOB PRIMARY KEY ON CONFLICT REPLACE,"_ID" TEXT,"_Level" TEXT,"_Layers" TEXT,"Transform" BLOB,"Id" TEXT,"Graphics" TEXT,"Placeholder" TEXT,"Physics" TEXT,"PhysicCategory" TEXT,"Name" TEXT,"LookAtText" TEXT,"ScriptPreset" TEXT,"ScriptOverride" TEXT,"CanUse" INTEGER,"CanDestroy" INTEGER,"Description" TEXT,"PickingRange" REAL,"PickingHeight" REAL,"UseAnim" TEXT,"TrackByMiniMap" INTEGER,"DwarfNoseDifficulty" INTEGER,"InfoIdentified" TEXT);
CREATE INDEX _Instance_LayLabShrine__Level ON _Instance_LayLabShrine ( _Level );
CREATE INDEX _Instance_LayLabShrine_Id ON _Instance_LayLabShrine ( Id );
CREATE INDEX _Instance_LayLabShrine_Name ON _Instance_LayLabShrine ( Name );
INSERT INTO _Instance_LayLabShrine ("Id","Graphics","Placeholder","Physics","PhysicCategory","Name","LookAtText","ScriptPreset","ScriptOverride","CanUse","CanDestroy","Description","PickingRange","PickingHeight","UseAnim","TrackByMiniMap","DwarfNoseDifficulty","InfoIdentified","Guid","_ID","_Level","_Layers","Transform") VALUES ('lab_shrine','_location_all_elements/altar','_location_04_elements/grab_03_inschrift','_location_all_elements/altar','Environment','lab_shrine','lookat_lab_shrine','','on:Use:lab_altar_use.xml',1,0,'',2.0,1.0,'Nehmen',0,0,'',X'CDAC60AF95135EDCBBFA91E80D7FF06D','|Level|Objects|LayLabShrine|lab_shrine','location01','',X'0000803F000000000000000000000000000000000000803F000000000000000000000000000000000000803F00000000626B53C35D2D4F40984245430000803F');
COMMIT;
