"""Write Install.bat / Uninstall.bat (CRLF) and copy sqlite3.exe into a mod folder.
Usage: python -I tools/make_bats.py <mod_dir> <backup_name> "<one-line description>"
"""
import sys, os, shutil
mod, backup, title = sys.argv[1], sys.argv[2], sys.argv[3]
HEAD = rf'''@echo off
:: {title}
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
'''
# own backup only when run by hand: the pack installer (which passes nopause) already saved everything to before_reinstall
SKIP = '' if backup == 'armory_backup' else 'if /i not "%~1"=="nopause" '   # armory_backup is the pack baseline: always made
INSTALL = HEAD + rf'''{SKIP}if not exist "%DB%\{backup}\game.db4" (
  mkdir "%DB%\{backup}" 2>nul
  copy /Y "%DB%\*.db4" "%DB%\{backup}\" >nul || ( echo Backup failed. Nothing was changed. & goto end )
  echo Backup of the databases saved in %DB%\{backup}
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
echo ERROR: a step failed. Run Uninstall.bat, or restore the files from %DB%\{backup}
:end
if /i not "%~1"=="nopause" pause
'''
UNINSTALL = HEAD + rf'''"%SQ%" -bail "%DB%\static.db4" < "%S%\undo_static.sql" || goto fail
"%SQ%" -bail "%DB%\locale.db4" < "%S%\undo_locale.sql" || goto fail
"%SQ%" -bail "%DB%\game.db4"   < "%S%\undo_game.sql"   || goto fail
if exist "%~dp0icons\files.txt" for /f "usebackq delims=" %%f in ("%~dp0icons\files.txt") do if exist "%ICO%\%%f" del "%ICO%\%%f"
if exist "%~dp0loose_files.txt" for /f "usebackq delims=" %%f in ("%~dp0loose_files.txt") do if exist "%GAME%\export\%%f" del "%GAME%\export\%%f"
echo.
echo Verification (expect 0 for the mod's rows):
"%SQ%" "%DB%\static.db4" < "%S%\verify_static.sql"
"%SQ%" "%DB%\game.db4"   < "%S%\verify_game.sql"
echo Removed. The backup in %DB%\{backup} is kept.
goto end
:fail
echo ERROR: a step failed. Restore the files from %DB%\{backup}
:end
if /i not "%~1"=="nopause" pause
'''
for name, text in (('Install.bat', INSTALL), ('Uninstall.bat', UNINSTALL)):
    with open(os.path.join(mod, name), 'w', encoding='ascii', newline='\r\n') as f: f.write(text)
shutil.copy(os.path.join(os.path.dirname(__file__), 'bin', 'sqlite3.exe'), mod)
print('ok', mod)
