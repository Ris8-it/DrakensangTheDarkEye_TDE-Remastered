@echo off
:: Removes every Drakensang TDE - Remastered module. Close the game first.
:: Restores the clean databases saved before the pack was first installed (export\db\armory_backup);
:: without that backup, each module is removed in reverse order instead. Saves are never touched.
setlocal
set "M=%~dp0..\"
if not defined DRAKENSANG set "DRAKENSANG=D:\Steam\steamapps\common\Drakensang"
set "DB=%DRAKENSANG%\export\db"
set "CLEAN=%DB%\armory_backup"
set "SYS=%SystemRoot%\System32"
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
if exist "%CLEAN%\static.db4" if exist "%CLEAN%\locale.db4" if exist "%CLEAN%\game.db4" (
  mkdir "%DB%\before_reinstall" 2>nul
  copy /Y "%DB%\*.db4" "%DB%\before_reinstall\" >nul
  copy /Y "%CLEAN%\static.db4" "%DB%\" >nul && copy /Y "%CLEAN%\locale.db4" "%DB%\" >nul && copy /Y "%CLEAN%\game.db4" "%DB%\" >nul && ( echo Drakensang TDE - Remastered removed. & goto end )
  echo Restore failed. Your previous databases are in %DB%\before_reinstall
  goto end
)
for %%o in (secret_quests quest_avestrue hard_ending remastered_systems arcane_thief armory_v2) do (
  echo ===== %%o =====
  call "%M%%%o\Uninstall.bat" nopause
)
echo Drakensang TDE - Remastered removed.
:end
if /i not "%~1"=="nopause" pause
