#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для автоматической установки и запуска бота локально
"""
import os
import sys
import subprocess
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_python():
    """Проверка версии Python"""
    if sys.version_info < (3, 9):
        print("[ОШИБКА] Требуется Python 3.9 или выше")
        sys.exit(1)
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def create_venv():
    """Создание виртуального окружения"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("[OK] Виртуальное окружение уже существует")
        return True
    
    print("[1/4] Создание виртуального окружения...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("[OK] Виртуальное окружение создано")
    return True

def get_venv_python():
    """Получение пути к Python в виртуальном окружении"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Linux/Mac
        return Path("venv/bin/python")

def install_dependencies():
    """Установка зависимостей"""
    venv_python = get_venv_python()
    if not venv_python.exists():
        print("[ОШИБКА] Виртуальное окружение не найдено")
        return False
    
    print("[2/4] Установка зависимостей...")
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "req.txt"], check=True)
    print("[OK] Зависимости установлены")
    return True

def check_env_file():
    """Проверка и создание .env файла"""
    env_path = Path(".env")
    if env_path.exists():
        print("[OK] Файл .env найден")
        return True
    
    print("[ВНИМАНИЕ] Файл .env не найден")
    print("\n" + "="*50)
    print("Создание файла .env")
    print("="*50)
    
    bot_token = input("Введите BOT_TOKEN (от @BotFather): ").strip()
    if not bot_token:
        print("[ОШИБКА] BOT_TOKEN обязателен!")
        return False
    
    admin_ids = input("Введите ADMIN_IDS (через запятую, Enter для значения по умолчанию): ").strip()
    if not admin_ids:
        admin_ids = "6177558353"
    
    use_sqlite = input("Использовать SQLite для локальной БД? (y/n, по умолчанию y): ").strip().lower()
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"BOT_TOKEN={bot_token}\n")
        f.write(f"ADMIN_IDS={admin_ids}\n")
        if use_sqlite != 'n':
            f.write("DATABASE_URL=sqlite+aiosqlite:///./mainercrypto.db\n")
        else:
            print("\nДля PostgreSQL укажите в .env:")
            print("POSTGRES_USER=postgres")
            print("POSTGRES_PASSWORD=postgres")
            print("POSTGRES_HOST=localhost")
            print("POSTGRES_NAME=mainercrypto")
    
    print("[OK] Файл .env создан")
    return True

def run_bot():
    """Запуск бота"""
    venv_python = get_venv_python()
    print("\n" + "="*50)
    print("[3/4] Запуск бота...")
    print("Для остановки нажмите Ctrl+C")
    print("="*50 + "\n")
    
    try:
        subprocess.run([str(venv_python), "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n[СТОП] Бот остановлен")
    except subprocess.CalledProcessError as e:
        print(f"\n[ОШИБКА] Ошибка при запуске: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    print("="*50)
    print("Установка и запуск MainerCrypto бота")
    print("="*50 + "\n")
    
    # Проверка Python
    check_python()
    
    # Создание виртуального окружения
    if not create_venv():
        return
    
    # Установка зависимостей
    if not install_dependencies():
        return
    
    # Проверка .env файла
    print("[3/4] Проверка .env файла...")
    if not check_env_file():
        return
    
    # Запуск бота
    print("[4/4] Запуск бота...")
    run_bot()

if __name__ == "__main__":
    main()

