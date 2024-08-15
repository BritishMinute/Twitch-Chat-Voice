@echo off
:: Check if the script is running with administrative privileges
if "%~1"=="ELEV" (
    :: Run the Python script
    python "your path here"
    goto :EOF
)

:: Request administrative privileges
set "params=%*"
powershell -Command "Start-Process '%~0' -ArgumentList 'ELEV %params%' -Verb RunAs"
