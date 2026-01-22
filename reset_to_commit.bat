@echo off
chcp 65001 >nul
echo Откат проекта к коммиту c077b9c...
git reset --hard c077b9c
if %errorlevel% equ 0 (
    echo Откат выполнен успешно!
) else (
    echo Ошибка при откате. Проверьте, что коммит c077b9c существует.
)
pause
