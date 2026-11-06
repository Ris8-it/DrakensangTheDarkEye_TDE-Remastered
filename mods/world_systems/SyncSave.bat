@echo off
:: World Systems: put this module's world content into your NEWEST save (any name). Save in game, quit, run this, load that save.
:: A backup of the save is kept next to it (.before_world_systems). Run Install.bat first.
setlocal
set "SQ=%~dp0sqlite3.exe"
set "SYS=%SystemRoot%\System32"
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
set "DSA="
for /f "delims=" %%f in ('powershell -NoProfile -Command "(Get-ChildItem -LiteralPath $env:USERPROFILE\Documents\Drakensang\profiles\default\save -Recurse -Filter *.dsa | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName"') do set "DSA=%%f"
if not defined DSA ( echo No save found. & goto end )
echo Save: %DSA%
copy /Y "%DSA%" "%DSA%.before_world_systems" >nul || ( echo Backup failed. Nothing was changed. & goto end )
"%SQ%" -bail "%DSA%" < "%~dp0sql\game.sql" || ( echo ERROR. Your backup: %DSA%.before_world_systems & goto end )
"%SQ%" "%DSA%" < "%~dp0sql\verify_game.sql"
"%SQ%" -bail "%DSA%" "VACUUM;"
echo Done. Load this save. Backup kept as %DSA%.before_world_systems
:end
if /i not "%~1"=="nopause" pause
