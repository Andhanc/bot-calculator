#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Анализ калькулятора доходности майнинга
Выявляет проблемы с расчетами
"""

def analyze_calculator():
    print("="*60)
    print("АНАЛИЗ КАЛЬКУЛЯТОРА ДОХОДНОСТИ МАЙНИНГА")
    print("="*60)
    
    print("\n1. ПРОБЛЕМА С ЕДИНИЦАМИ ИЗМЕРЕНИЯ ХЕШРЕЙТА")
    print("-"*60)
    print("""
    КРИТИЧЕСКАЯ ПРОБЛЕМА: Несоответствие единиц измерения!
    
    В базе данных network_hashrate хранится в разных единицах:
    - SHA-256: 650_000_000 (предположительно TH/s, но это 650 PH/s)
    - Scrypt: 600_000 (предположительно MH/s = 0.6 TH/s)
    - Etchash: 50_000_000 (предположительно MH/s = 50 TH/s)
    - kHeavyHash: 300_000 (предположительно GH/s = 300 TH/s)
    
    В калькуляторе (строка 50-53):
    ```python
    miner_hash = hash_rate  # Берется из модели ASIC
    network_hash = info["network_hashrate"]  # Из базы данных
    share = miner_hash / network_hash  # ❌ ОШИБКА: единицы не совпадают!
    ```
    
    ПРОБЛЕМА: Если miner_hash в TH/s, а network_hash в MH/s или GH/s,
    расчет share будет неверным!
    """)
    
    print("\n2. ПРОБЛЕМА С РАСЧЕТОМ МОНЕТ")
    print("-"*60)
    print("""
    В функции make_period (строка 73):
    ```python
    coins = (daily_income_usd / coin["price"]) * multiplier
    ```
    
    ПРОБЛЕМА: Это неправильно! Нужно использовать daily_coins напрямую:
    ```python
    coins = daily_coins * multiplier
    ```
    
    Текущая формула дает неправильный результат для нескольких монет,
    так как daily_income_usd уже рассчитан для первой монеты.
    """)
    
    print("\n3. ПРОБЛЕМА С НОРМАЛИЗАЦИЕЙ ЕДИНИЦ")
    print("-"*60)
    print("""
    Код не нормализует единицы измерения перед расчетом.
    
    Нужно:
    1. Определить единицы miner_hash (из параметров алгоритма)
    2. Определить единицы network_hash (из параметров алгоритма)
    3. Привести к одной единице (например, H/s)
    4. Только потом делить
    
    Пример правильного расчета:
    ```python
    # Конвертация в H/s для унификации
    unit_multipliers = {
        "th/s": 1_000_000_000_000,  # TH/s -> H/s
        "gh/s": 1_000_000_000,      # GH/s -> H/s
        "mh/s": 1_000_000,          # MH/s -> H/s
        "h/s": 1                     # H/s -> H/s
    }
    
    miner_hash_hs = miner_hash * unit_multipliers[unit]
    network_hash_hs = network_hash * unit_multipliers[network_unit]
    share = miner_hash_hs / network_hash_hs
    ```
    """)
    
    print("\n4. ПРОБЛЕМА С БЛОК-ТАЙМОМ")
    print("-"*60)
    print("""
    Для kHeavyHash используется фиксированное значение:
    ```python
    if algorithm.lower() == "kheavyhash":
        blocks_per_day = 86400  # 1 блок в секунду
    ```
    
    Это правильно, но для других алгоритмов:
    ```python
    blocks_per_day = 86400 / algo_params["block_time"]
    ```
    
    ПРОБЛЕМА: block_time в секундах, но нужно убедиться, что значения правильные:
    - SHA-256: 600 сек (10 мин) ✓
    - Scrypt: 150 сек (2.5 мин) - проверить!
    - Etchash: 13 сек - проверить!
    """)
    
    print("\n5. ПРОБЛЕМА С EFFICIENCY_FACTOR")
    print("-"*60)
    print("""
    В коде используется efficiency_factor = 1.0 для всех алгоритмов.
    
    Это означает, что не учитываются:
    - Потери на пуле (обычно 1-2%)
    - Задержки сети
    - Неидеальная работа оборудования
    
    Возможно, нужно установить efficiency_factor = 0.98-0.99
    """)
    
    print("\n6. РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ")
    print("-"*60)
    print("""
    1. ✅ Нормализовать единицы измерения перед расчетом share
    2. ✅ Исправить расчет coins_per_coin (использовать daily_coins)
    3. ✅ Убедиться, что network_hashrate в базе в правильных единицах
    4. ✅ Добавить проверку единиц измерения
    5. ✅ Рассмотреть добавление efficiency_factor < 1.0
    6. ✅ Добавить логирование для отладки расчетов
    """)
    
    print("\n" + "="*60)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*60)

if __name__ == "__main__":
    analyze_calculator()

