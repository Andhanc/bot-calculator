#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для изменения BOT_TOKEN в .env файле
"""
import os
import re
from pathlib import Path

def change_token():
    env_file = Path('.env')
    
    if not env_file.exists():
        print("[ОШИБКА] Файл .env не найден!")
        return False
    
    # Читаем текущий файл
    content = env_file.read_text(encoding='utf-8')
    
    # Показываем текущий токен
    current_token_match = re.search(r'BOT_TOKEN\s*=\s*[\'"]?([^\'"\n]+)', content)
    if current_token_match:
        current_token = current_token_match.group(1).strip("'\"")
        print(f"Текущий BOT_TOKEN: {current_token[:20]}...")
    else:
        print("Текущий BOT_TOKEN не найден в файле")
    
    # Запрашиваем новый токен
    print("\n" + "="*50)
    new_token = input("Введите новый BOT_TOKEN: ").strip()
    
    if not new_token:
        print("[ОШИБКА] Токен не может быть пустым!")
        return False
    
    # Заменяем токен в файле
    # Ищем строку с BOT_TOKEN и заменяем значение
    pattern = r'(BOT_TOKEN\s*=\s*)[\'"]?[^\'"\n]+[\'"]?'
    replacement = r'\1' + new_token
    
    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Если не нашлось, добавляем в конец
    if new_content == content:
        if 'BOT_TOKEN' not in content.upper():
            new_content = content + f"\nBOT_TOKEN={new_token}\n"
        else:
            print("[ОШИБКА] Не удалось найти BOT_TOKEN для замены")
            return False
    
    # Сохраняем файл
    env_file.write_text(new_content, encoding='utf-8')
    print("\n[OK] Токен успешно изменен!")
    print(f"Новый BOT_TOKEN: {new_token[:20]}...")
    return True

if __name__ == "__main__":
    try:
        change_token()
    except KeyboardInterrupt:
        print("\n\n[ОТМЕНА] Операция отменена")
    except Exception as e:
        print(f"\n[ОШИБКА] {e}")

