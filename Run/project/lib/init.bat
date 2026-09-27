@echo off

set "RUN_DIR=%~dp0\.."

for %%i in ("%RUN_DIR%..") do set "ROOT_DIR=%%~fi"

set "SCRIPTS_DIR=%ROOT_DIR%\scripts"
set "DB=%ROOT_DIR%\db\movies.duckdb"

cd /d "%ROOT_DIR%"

echo Root: %ROOT_DIR%
echo Scripts: %SCRIPTS_DIR%
echo.