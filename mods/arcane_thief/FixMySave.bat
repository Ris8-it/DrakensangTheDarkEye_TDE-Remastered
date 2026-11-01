@echo off
:: Drakensang TDE - Remastered: fixes for a game started with the earlier pack (patches your NEWEST save, any name).
:: 1. Arcane Thief: the starting spells the game drops at character creation (Axxeleratus 3, Blitz 3, Duplicatus 2, Fulminictus 2).
:: 2. New NPCs (Ulfried etc.): removes a walking routine copied from the Tallon hunter (crash "PerformFollowPath ... loc08_path_jaeger").
:: 3. Spellguard / Nightfox / Mirror bucklers you already own: made of wood, so they no longer block spellcasting.
:: Use: save in game, quit the game, run this, load that save. A backup of the save is kept.
setlocal
set "SAVES=%USERPROFILE%\Documents\Drakensang\profiles\default\save"
set "SQ=%~dp0sqlite3.exe"
set "SYS=%SystemRoot%\System32"
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
set "DSA="
for /f "delims=" %%f in ('powershell -NoProfile -Command "(Get-ChildItem -LiteralPath $env:USERPROFILE\Documents\Drakensang\profiles\default\save -Recurse -Filter *.dsa | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName"') do set "DSA=%%f"
if not defined DSA ( echo No save found in %SAVES% & goto end )
echo Save: %DSA%
copy /Y "%DSA%" "%DSA%.before_fix" >nul || ( echo Backup failed. Nothing was changed. & goto end )
"%SQ%" -bail "%DSA%" "UPDATE _Instance_PC SET ZaAxxeleratus=3 WHERE Advantages LIKE '%%z_arcanethief%%' AND ZaAxxeleratus<0; UPDATE _Instance_PC SET ZaBlitz=3 WHERE Advantages LIKE '%%z_arcanethief%%' AND ZaBlitz<0; UPDATE _Instance_PC SET ZaDuplicatus=2 WHERE Advantages LIKE '%%z_arcanethief%%' AND ZaDuplicatus<0; UPDATE _Instance_PC SET ZaFulminictus=2 WHERE Advantages LIKE '%%z_arcanethief%%' AND ZaFulminictus<0; UPDATE _Instance_NPC SET BaseActionScript='', BaseAction='', CurrAction='v*;2;false;false;' WHERE Id LIKE 'arm!_npc!_%%' ESCAPE '!'; UPDATE _Instance_Shield SET ArMaterial='Wood' WHERE Id IN ('arm_r_spellguard','arm_a_nightfox_buckler','arm_s_mirror_buckler');" || ( echo ERROR. Your backup: %DSA%.before_fix & goto end )
"%SQ%" "%DSA%" "SELECT 'Arcane Thief found: ' || count(*) || '   Axxeleratus ' || max(ZaAxxeleratus) || ', Blitz ' || max(ZaBlitz) || ', Duplicatus ' || max(ZaDuplicatus) || ', Fulminictus ' || max(ZaFulminictus) FROM _Instance_PC WHERE Advantages LIKE '%%z_arcanethief%%'; SELECT 'New NPCs with a walking routine left: ' || count(*) FROM _Instance_NPC WHERE Id LIKE 'arm!_npc!_%%' ESCAPE '!' AND (BaseActionScript<>'' OR CurrAction LIKE '%%FollowPath%%');"
echo Done. Load this save. Backup kept as %DSA%.before_fix
:end
pause
