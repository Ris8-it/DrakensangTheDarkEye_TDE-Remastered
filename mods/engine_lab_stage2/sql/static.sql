BEGIN;
DROP TABLE IF EXISTS "_Template_LayLabShrine";
CREATE TABLE '_Template_LayLabShrine' ( "Id" TEXT PRIMARY KEY ON CONFLICT REPLACE,"Graphics" TEXT,"Placeholder" TEXT,"Physics" TEXT,"PhysicCategory" TEXT,"Name" TEXT,"LookAtText" TEXT,"ScriptPreset" TEXT,"ScriptOverride" TEXT,"CanUse" INTEGER,"CanDestroy" INTEGER,"Description" TEXT,"PickingRange" REAL,"PickingHeight" REAL,"UseAnim" TEXT,"TrackByMiniMap" INTEGER,"DwarfNoseDifficulty" INTEGER,"InfoIdentified" TEXT);
CREATE INDEX _Template_LayLabShrine_Name ON _Template_LayLabShrine ( Name );
INSERT INTO _Categories ("CategoryName","IsVirtualCategory","IsSpecialCategory","CategoryTemplateTable","CategoryInstanceTable") VALUES ('LayLabShrine',0,0,'_Template_LayLabShrine','_Instance_LayLabShrine');
INSERT INTO _Template_LayLabShrine ("Id","Graphics","Placeholder","Physics","PhysicCategory","Name","LookAtText","ScriptPreset","ScriptOverride","CanUse","CanDestroy","Description","PickingRange","PickingHeight","UseAnim","TrackByMiniMap","DwarfNoseDifficulty","InfoIdentified") VALUES ('lab_shrine','_location_all_elements/altar','_location_04_elements/grab_03_inschrift','_location_all_elements/altar','Environment','lab_shrine','lookat_lab_shrine','','on:Use:lab_altar_use.xml',1,0,'',2.0,1.0,'Nehmen',0,0,'');
COMMIT;
