"""
Тестовый скрипт для проверки совпадения расчетов ASIC-майнеров с расчетами по хэшрейту
"""
import asyncio
from database.models import CreateDatabase, AsicModel, AsicModelLine, Algorithm
from config import get_db_url
from utils.calculator import MiningCalculator
from sqlalchemy import select


async def test_asic_vs_hashrate():
    """Сравнение расчетов ASIC-майнеров с расчетами по хэшрейту"""
    db_manager = CreateDatabase(database_url=get_db_url())
    await db_manager.async_main()
    
    # Тестовые параметры
    electricity_price_rub = 5.0
    usd_to_rub = 100.0
    pool_fee = 0.015  # 1.5%
    
    async with db_manager.async_session() as session:
        # Выбираем несколько ASIC-майнеров для тестирования
        test_models = [
            ("Bitmain Antminer S19 100 TH/s", Algorithm.SHA256, 100),  # SHA-256
            ("Bitmain Antminer L7 9500 MH/s", Algorithm.SCRYPT, 9500),  # Scrypt
            ("Bitmain Antminer E9 Pro 3780 MH/s", Algorithm.ETCHASH, 3780),  # Etchash
            ("Bitmain Antminer KAS Miner KS5", Algorithm.KHEAVYHASH, 20),  # kHeavyHash
            ("Bitmain Antminer KA3 173 TH/s", Algorithm.BLAKE2S, 173),  # Blake2S
        ]
        
        print("=" * 80)
        print("СРАВНЕНИЕ РАСЧЕТОВ ASIC-МАЙНЕРОВ С РАСЧЕТАМИ ПО ХЭШРЕЙТУ")
        print("=" * 80)
        
        for model_name, algorithm, expected_hashrate in test_models:
            print(f"\n{'='*80}")
            print(f"Модель: {model_name}")
            print(f"Алгоритм: {algorithm.value}")
            print(f"Ожидаемый хэшрейт: {expected_hashrate}")
            
            # Получаем данные алгоритма
            from database.models import AlgorithmData
            algo_result = await session.execute(
                select(AlgorithmData).where(AlgorithmData.algorithm == algorithm)
            )
            algo_data = algo_result.scalar_one()
            
            # Получаем монету
            from database.models import Coin
            coin_result = await session.execute(
                select(Coin).where(Coin.symbol == algo_data.default_coin)
            )
            coin = coin_result.scalar_one()
            
            print(f"Монета: {coin.symbol}")
            print(f"Network hashrate: {algo_data.network_hashrate}")
            print(f"Block reward: {algo_data.block_reward}")
            # block_time берется из algo_params, если не указан в coin_data
            algo_params = MiningCalculator.get_algorithm_params(algorithm.value.lower())
            block_time = algo_params.get("block_time", 600)
            print(f"Block time: {block_time} сек")
            
            # Расчет для ASIC-майнера (hash_rate в единицах из базы данных)
            asic_result = MiningCalculator.calculate_profitability(
                hash_rate=expected_hashrate,
                power_consumption=3250,  # Примерное потребление
                electricity_price_rub=electricity_price_rub,
                coin_data={
                    coin.symbol: {
                        "price": coin.current_price_usd,
                        "network_hashrate": algo_data.network_hashrate,
                        "block_reward": algo_data.block_reward,
                        "algorithm": algorithm.value.lower(),
                        "block_time": block_time,
                    }
                },
                usd_to_rub=usd_to_rub,
                algorithm=algorithm.value.lower(),
            )
            
            # Расчет для ручного ввода хэшрейта (в единицах, указанных в algo_params)
            algo_params = MiningCalculator.get_algorithm_params(algorithm.value.lower())
            manual_hashrate = expected_hashrate
            
            # Конвертируем в единицы для ручного ввода, если нужно
            if algorithm == Algorithm.SCRYPT:
                # Для Scrypt: если hash_rate > 1000, это MH/s, нужно конвертировать в GH/s для ручного ввода
                # Но для ручного ввода используется MH/s согласно hashrate_unit
                # На самом деле, для ручного ввода пользователь вводит в GH/s (согласно handlers/client.py)
                # Но в algo_params указано "mh/s" - это несоответствие!
                # Для теста используем то же значение
                pass
            elif algorithm == Algorithm.ETCHASH:
                # Для Etchash: если hash_rate < 100, это GH/s, иначе MH/s
                # Для ручного ввода используется GH/s
                if manual_hashrate >= 100:  # Это MH/s
                    manual_hashrate = manual_hashrate / 1000  # MH/s -> GH/s
            
            manual_result = MiningCalculator.calculate_profitability(
                hash_rate=manual_hashrate,
                power_consumption=3250,
                electricity_price_rub=electricity_price_rub,
                coin_data={
                    coin.symbol: {
                        "price": coin.current_price_usd,
                        "network_hashrate": algo_data.network_hashrate,
                        "block_reward": algo_data.block_reward,
                        "algorithm": algorithm.value.lower(),
                        "block_time": block_time,
                    }
                },
                usd_to_rub=usd_to_rub,
                algorithm=algorithm.value.lower(),
            )
            
            # Сравнение результатов
            asic_daily_coins = asic_result["periods"]["day"]["coins_per_coin"][coin.symbol]
            manual_daily_coins = manual_result["periods"]["day"]["coins_per_coin"][coin.symbol]
            
            print(f"\nРезультаты:")
            print(f"  ASIC (hash_rate={expected_hashrate}):")
            print(f"    Монет/день: {asic_daily_coins:.8f} {coin.symbol}")
            print(f"    Доход USD/день: ${asic_result['periods']['day']['income_usd']:.2f}")
            print(f"  Ручной ввод (hash_rate={manual_hashrate}):")
            print(f"    Монет/день: {manual_daily_coins:.8f} {coin.symbol}")
            print(f"    Доход USD/день: ${manual_result['periods']['day']['income_usd']:.2f}")
            
            diff = abs(asic_daily_coins - manual_daily_coins)
            diff_percent = (diff / asic_daily_coins * 100) if asic_daily_coins > 0 else 0
            
            if diff < 0.00000001:  # Практически одинаково
                print(f"  ✅ РАСЧЕТЫ СОВПАДАЮТ (разница: {diff:.10f})")
            else:
                print(f"  ⚠️ РАСЧЕТЫ НЕ СОВПАДАЮТ (разница: {diff:.10f}, {diff_percent:.4f}%)")


if __name__ == "__main__":
    asyncio.run(test_asic_vs_hashrate())

