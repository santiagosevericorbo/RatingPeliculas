@echo off

REM ================================
REM CSV -> Parquet (DuckDB)
REM ================================

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

cd /d "%ROOT_DIR%"

set "DB=db\movies.duckdb"

echo Convirtiendo CSV a Parquet...

db\duckdb.exe "%DB%" ^
 -c "COPY (SELECT * FROM read_csv_auto('data/letterboxd/letterboxd_movies.csv')) TO 'data/letterboxd/letterboxd_movies.parquet' (FORMAT PARQUET);"

echo.
echo Conversion finalizada.
pause