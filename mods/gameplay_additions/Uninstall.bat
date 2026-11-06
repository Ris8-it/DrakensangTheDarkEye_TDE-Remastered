@echo off
:: Gameplay Additions by mg979 (v2.1b, mild preset), part of Drakensang TDE - Remastered: class rules, loot, monsters, spells, lights, ambience.
:: Safe to run more than once. Add "nopause" to skip the final pause.
setlocal
if not defined DRAKENSANG set "DRAKENSANG=D:\Steam\steamapps\common\Drakensang"
set "GAME=%DRAKENSANG%"
set "DB=%GAME%\export\db"
set "ICO=%GAME%\export\textures\icons"
set "SQ=%~dp0sqlite3.exe"
set "S=%~dp0sql"
set "SYS=%SystemRoot%\System32"
if not exist "%DB%\static.db4" ( echo Cannot find %DB% & goto end )
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
"%SQ%" -bail "%DB%\static.db4" < "%S%\undo_static.sql" || goto fail
"%SQ%" -bail "%DB%\locale.db4" < "%S%\undo_locale.sql" || goto fail
"%SQ%" -bail "%DB%\game.db4"   < "%S%\undo_game.sql"   || goto fail
if exist "%~dp0icons\files.txt" for /f "usebackq delims=" %%f in ("%~dp0icons\files.txt") do if exist "%ICO%\%%f" del "%ICO%\%%f"
if exist "%~dp0loose_files.txt" for /f "usebackq delims=" %%f in ("%~dp0loose_files.txt") do if exist "%GAME%\export\%%f" del "%GAME%\export\%%f"
echo.
echo Verification (expect 0 for the mod's rows):
"%SQ%" "%DB%\static.db4" < "%S%\verify_static.sql"
"%SQ%" "%DB%\game.db4"   < "%S%\verify_game.sql"
echo Removed. The backup in %DB%\gameplay_additions_backup is kept.
goto end
:fail
echo ERROR: a step failed. Restore the files from %DB%\gameplay_additions_backup
:end
if /i not "%~1"=="nopause" pause
