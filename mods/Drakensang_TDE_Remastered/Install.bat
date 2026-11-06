@echo off
:: Drakensang TDE - Remastered: installs every module in order. Close the game first. Start a NEW game afterwards.
:: Safe to run more than once. Each run starts from the clean databases saved before the pack was first installed
:: (export\db\armory_backup), so nothing from an older version of the pack is left behind.
:: Includes mg979's Gameplay Additions v2.1b (first module): no need to install it separately; harmless if you already did.
:: Hard Ending, Unofficial Patch, World Systems and Smarter Foes are put back automatically if they were installed. Saves are never touched.
setlocal
set "M=%~dp0..\"
if not defined DRAKENSANG set "DRAKENSANG=D:\Steam\steamapps\common\Drakensang"
set "DB=%DRAKENSANG%\export\db"
set "CLEAN=%DB%\armory_backup"
set "SQ=%~dp0sqlite3.exe"
set "SYS=%SystemRoot%\System32"
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
set "HARD="
for /f "usebackq" %%v in (`call "%SQ%" "%DB%\static.db4" ^< "%~dp0hard_check.sql"`) do set "LIVE=%%v"
for /f "usebackq" %%v in (`call "%SQ%" "%CLEAN%\static.db4" ^< "%~dp0hard_check.sql"`) do set "BASE=%%v"
if defined LIVE if defined BASE if not "%LIVE%"=="%BASE%" set "HARD=1"
:: optional engine-layer modules: reinstalled if their state machine is in the live database
for %%o in (unofficial_patch world_systems smarter_foes) do for /f "usebackq" %%v in (`call "%SQ%" "%DB%\static.db4" ^< "%~dp0%%o_check.sql"`) do if not "%%v"=="0" set "OPT_%%o=1"
if exist "%CLEAN%\static.db4" if exist "%CLEAN%\locale.db4" if exist "%CLEAN%\game.db4" (
  echo ===== restoring the clean databases =====
  mkdir "%DB%\before_reinstall" 2>nul
  copy /Y "%DB%\*.db4" "%DB%\before_reinstall\" >nul
  copy /Y "%CLEAN%\static.db4" "%DB%\" >nul || goto fail
  copy /Y "%CLEAN%\locale.db4" "%DB%\" >nul || goto fail
  copy /Y "%CLEAN%\game.db4" "%DB%\" >nul || goto fail
) else (
  echo ===== removing Armory v1 (if present) =====
  if exist "%M%armory\Uninstall.bat" call "%M%armory\Uninstall.bat" nopause
  echo ===== saving your clean databases in %CLEAN% =====
  mkdir "%CLEAN%" 2>nul
  copy /Y "%DB%\*.db4" "%CLEAN%\" >nul || ( echo Backup failed. Nothing was changed. & goto end )
)
for %%o in (gameplay_additions armory_v2 arcane_thief remastered_systems quest_avestrue secret_quests) do (
  echo ===== %%o =====
  call "%M%%%o\Install.bat" nopause || goto fail
)
if defined HARD (
  echo ===== hard_ending (was installed) =====
  call "%M%hard_ending\Install.bat" nopause || goto fail
)
for %%o in (unofficial_patch world_systems smarter_foes) do (
  if defined OPT_%%o (
    echo ===== %%o (was installed) =====
    call "%M%%%o\Install.bat" nopause || goto fail
  )
)
echo.
echo Drakensang TDE - Remastered installed. Optional: Install_HardEnding.bat for tougher late enemies.
goto end
:fail
echo ERROR during install. Your previous databases are in %DB%\before_reinstall
:end
if /i not "%~1"=="nopause" pause
