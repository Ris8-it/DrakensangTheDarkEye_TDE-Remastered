@echo off
:: Arcane Thief: Thief archetype becomes a dagger/magic hybrid (new heroes).
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
for /f "usebackq delims=" %%f in ("%~dp0icons\files.txt") do if exist "%ICO%\%%f" del "%ICO%\%%f"
echo.
echo Verification (expect 0 for the mod's rows):
"%SQ%" "%DB%\static.db4" < "%S%\verify_static.sql"
"%SQ%" "%DB%\game.db4"   < "%S%\verify_game.sql"
echo Removed. The backup in %DB%\arcanethief_backup is kept.
goto end
:fail
echo ERROR: a step failed. Restore the files from %DB%\arcanethief_backup
:end
if /i not "%~1"=="nopause" pause
