@echo off

REM ================================
REM IMDb Pipeline DuckDB
REM ================================

cd /d "%~dp0.."

echo Ejecutando pipeline IMDb...

db\duckdb.exe db\movies.duckdb ^
 -c ".read scripts/02_clean_imdb_Rated.sql" ^
 -c ".read scripts/03_imdb_metrics_Rated.sql" ^
 -c ".read scripts/99_exports_Rated.sql"

echo.
echo Pipeline finalizado.
pause