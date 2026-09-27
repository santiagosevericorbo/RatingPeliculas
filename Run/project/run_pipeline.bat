@echo off
setlocal enabledelayedexpansion

echo =====================================
echo INICIANDO PIPELINE
echo =====================================

REM cargar config
call "%~dp0config.bat"

REM inicializar entorno
call "%~dp0lib\init.bat"

REM contar scripts
call "%~dp0lib\counter.bat"

REM ejecutar pipeline
call "%~dp0lib\executor.bat"

echo.
echo =====================================
echo PIPELINE COMPLETADO
echo =====================================

pause