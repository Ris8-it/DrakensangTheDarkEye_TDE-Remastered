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
if /i not "%~1"=="nopause" if not exist "%DB%\gameplay_additions_backup\game.db4" (
  mkdir "%DB%\gameplay_additions_backup" 2>nul
  copy /Y "%DB%\*.db4" "%DB%\gameplay_additions_backup\" >nul || ( echo Backup failed. Nothing was changed. & goto end )
  echo Backup of the databases saved in %DB%\gameplay_additions_backup
)
echo Installing...
"%SQ%" -bail "%DB%\static.db4" < "%S%\static.sql" || goto fail
"%SQ%" -bail "%DB%\locale.db4" < "%S%\locale.sql" || goto fail
"%SQ%" -bail "%DB%\game.db4"   < "%S%\game.sql"   || goto fail
if exist "%S%\clear_rhulana_tests.sql" "%SQ%" -bail "%DB%\game.db4" < "%S%\clear_rhulana_tests.sql" || goto fail
if exist "%~dp0icons\*.dds" copy /Y "%~dp0icons\*.dds" "%ICO%\" >nul || goto fail
if exist "%~dp0loose\" "%SYS%\xcopy.exe" /Y /E /I /Q "%~dp0loose" "%GAME%\export" >nul || goto fail
echo.
echo Verification:
"%SQ%" "%DB%\static.db4" < "%S%\verify_static.sql"
"%SQ%" "%DB%\locale.db4" < "%S%\verify_locale.sql"
"%SQ%" "%DB%\game.db4"   < "%S%\verify_game.sql"
echo.
echo Done. Start a NEW game to see the items.
goto end
:fail
echo ERROR: a step failed. Run Uninstall.bat, or restore the files from %DB%\gameplay_additions_backup
:end
if /i not "%~1"=="nopause" pause
