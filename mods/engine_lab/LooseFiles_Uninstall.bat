@echo off
:: Removes the loose data files of this module from your own game archives (nothing from the game is shipped).
:: Uses Python if installed (tested path), otherwise Windows PowerShell (same logic, loosefiles.ps1).
if not defined DRAKENSANG set "DRAKENSANG=D:\Steam\steamapps\common\Drakensang"
where py >nul 2>nul && ( py -3 -I "%~dp0loosefiles.py" remove "%~dp0loosefiles.json" "%DRAKENSANG%" & goto end )
where python >nul 2>nul && ( python -I "%~dp0loosefiles.py" remove "%~dp0loosefiles.json" "%DRAKENSANG%" & goto end )
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0loosefiles.ps1" -Game "%DRAKENSANG%" -Remove
:end
if /i not "%~1"=="nopause" pause
