@echo off

REM ================================
REM IMDb Pipeline DuckDB
REM ================================

cd /d "%~dp0.."

echo Ejecutando pipeline IMDb...

db\duckdb.exe db\movies.duckdb ^
 -c ".read scripts/2_clean/movies/imdb.sql" ^
 -c ".read scripts/03_imdb_metrics.sql" ^
 -c ".read scripts/99_export.sql"

db\duckdb.exe db\books.duckdb ^
 -c ".read scripts/99_exports/books/zlib_downloads.sql" ^
echo.
echo Pipeline finalizado.
pause