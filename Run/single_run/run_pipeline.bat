@echo off
setlocal enabledelayedexpansion

echo =====================================
echo INICIANDO PIPELINE
echo =====================================

REM ---- carpeta donde esta el BAT ----
set "RUN_DIR=%~dp0"

REM ---- subir un nivel (root proyecto) ----
for %%i in ("%RUN_DIR%..") do set "ROOT_DIR=%%~fi"

REM ---- carpeta scripts ----
set "SCRIPTS_DIR=%ROOT_DIR%\scripts"

REM ---- DB ----
set "DB=%ROOT_DIR%\db\movies.duckdb"

cd /d "%ROOT_DIR%"

echo Root: %ROOT_DIR%
echo Scripts: %SCRIPTS_DIR%
echo.

REM =====================================
REM contar scripts
REM =====================================

set COUNT=0
for /r "%SCRIPTS_DIR%" %%f in (*.sql) do (
    set /a COUNT+=1
)

echo Total scripts: !COUNT!
echo.

REM =====================================
REM ejecutar scripts
REM =====================================

set CURRENT=0

for /r "%SCRIPTS_DIR%" %%f in (*.sql) do (
    set /a CURRENT+=1

    set "FULLPATH=%%f"
    set "RELATIVE=!FULLPATH:%ROOT_DIR%\=!"

    echo -------------------------------------
    echo [!CURRENT!/!COUNT!] Ejecutando:
    echo !RELATIVE!
    echo -------------------------------------

    "%ROOT_DIR%\db\duckdb.exe" "%DB%" -c ".read '%%f'"

    if errorlevel 1 (
        echo ERROR en !RELATIVE!
        pause
        exit /b 1
    )
)

echo.
echo =====================================
echo PIPELINE COMPLETADO
echo =====================================

pause