@echo off
setlocal
set "OMPO_DIR=%~dp0"
if "%OMPO_DIR:~-1%"=="\" set "OMPO_DIR=%OMPO_DIR:~0,-1%"

set "XDG_CONFIG_HOME=%OMPO_DIR%\config"
set "XDG_DATA_HOME=%OMPO_DIR%\data"
set "NODE_PATH=%OMPO_DIR%\node_modules"

"%OMPO_DIR%\node_modules\.bin\opencode.cmd" %*
endlocal
