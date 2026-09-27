@echo off

set COUNT=0

for /r "%SCRIPTS_DIR%" %%f in (*.sql) do (

    set SKIP=0
    set "FULLPATH=%%f"

    for %%E in ("%EXCLUDE_1%" "%EXCLUDE_2%" "%EXCLUDE_3%") do (
        if not "%%~E"=="" (
            echo !FULLPATH! | find /i "%%~E" >nul && set SKIP=1
        )
    )

    if !SKIP! == 0 (
        set /a COUNT+=1
    )
)

echo Total scripts: !COUNT!
echo.