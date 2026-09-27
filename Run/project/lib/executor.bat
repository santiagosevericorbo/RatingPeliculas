@echo off

set CURRENT=0

for /r "%SCRIPTS_DIR%" %%f in (*.sql) do (

    set SKIP=0
    set "FULLPATH=%%f"

    for %%E in ("%EXCLUDE_1%" "%EXCLUDE_2%" "%EXCLUDE_3%") do (
        if not "%%~E"=="" (
            echo !FULLPATH! | find /i "%%~E" >nul && set SKIP=1
        )
    )

    if !SKIP! == 0 (

        set /a CURRENT+=1
        set "RELATIVE=!FULLPATH:%ROOT_DIR%\=!"

        echo -------------------------------------
        echo [!CURRENT!/!COUNT!] Ejecutando:
        echo !RELATIVE!
        echo -------------------------------------

        "%ROOT_DIR%\db\duckdb.exe" "%DB%" -c ".read '%%f'"

        if errorlevel 1 (
            echo ERROR en !RELATIVE!
            exit /b 1
        )
    )
)