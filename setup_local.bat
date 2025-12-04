@echo off
echo ========================================
echo Установка и запуск MainerCrypto бота
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не установлен!
    echo Установите Python 3.9+ с https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Создание виртуального окружения...
if not exist venv (
    python -m venv venv
    echo Виртуальное окружение создано
) else (
    echo Виртуальное окружение уже существует
)

echo.
echo [2/4] Активация виртуального окружения и установка зависимостей...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r req.txt

echo.
echo [3/4] Проверка .env файла...
if not exist .env (
    echo.
    echo ========================================
    echo ВНИМАНИЕ: Не найден файл .env
    echo ========================================
    echo.
    echo Создайте файл .env со следующим содержимым:
    echo.
    echo BOT_TOKEN=ваш_токен_бота
    echo ADMIN_IDS=6177558353
    echo.
    echo Для использования SQLite (рекомендуется для локального запуска):
    echo DATABASE_URL=sqlite+aiosqlite:///./mainercrypto.db
    echo.
    echo Или для PostgreSQL:
    echo POSTGRES_USER=postgres
    echo POSTGRES_PASSWORD=postgres
    echo POSTGRES_HOST=localhost
    echo POSTGRES_NAME=mainercrypto
    echo.
    set /p create_env="Создать .env файл сейчас? (y/n): "
    if /i "%create_env%"=="y" (
        set /p bot_token="Введите BOT_TOKEN: "
        echo BOT_TOKEN=%bot_token% > .env
        echo ADMIN_IDS=6177558353 >> .env
        echo DATABASE_URL=sqlite+aiosqlite:///./mainercrypto.db >> .env
        echo.
        echo Файл .env создан!
    ) else (
        echo Пожалуйста, создайте .env файл вручную и запустите скрипт снова.
        pause
        exit /b 1
    )
) else (
    echo Файл .env найден
)

echo.
echo [4/4] Запуск бота...
echo.
echo ========================================
echo Бот запускается...
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

python main.py

pause

