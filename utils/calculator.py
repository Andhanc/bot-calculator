# calculator.py
from datetime import datetime
from typing import Any, Dict, List


class MiningCalculator:
    # Множители для конвертации в H/s (хешей в секунду)
    UNIT_MULTIPLIERS = {
        "th/s": 1_000_000_000_000,  # TH/s -> H/s (терахеш)
        "gh/s": 1_000_000_000,      # GH/s -> H/s (гигахеш)
        "mh/s": 1_000_000,          # MH/s -> H/s (мегахеш)
        "kh/s": 1_000,              # KH/s -> H/s (килохеш)
        "h/s": 1                    # H/s -> H/s (хеш)
    }

    @staticmethod
    def get_algorithm_params(algorithm: str) -> Dict[str, float]:
        params = {
            "block_time": 600,
            "difficulty_factor": 1.0,
            "efficiency_factor": 1.0,  # Capminer.ru не использует efficiency_factor
            "hashrate_unit": "th/s"
        }

        algorithm_lower = algorithm.lower()

        if algorithm_lower in ["sha-256", "sha256"]:
            params.update({"hashrate_unit": "th/s", "block_time": 600})
        elif algorithm_lower in ["scrypt"]:
            params.update({"hashrate_unit": "mh/s", "block_time": 150})
        elif algorithm_lower in ["etchash", "ethash", "etchash/ethash"]:
            params.update({"hashrate_unit": "gh/s", "block_time": 13})  # На capminer.ru для Etchash используется GH/s
        elif algorithm_lower in ["kheavyhash"]:
            params.update({"hashrate_unit": "th/s", "block_time": 1})  # На capminer.ru для kHeavyHash используется TH/s
        elif algorithm_lower in ["blake2s"]:
            params.update({"hashrate_unit": "th/s", "block_time": 30})  # На capminer.ru для Blake2S используется TH/s
        elif algorithm_lower in ["blake2b+sha3", "blake2b_sha3"]:
            params.update({"hashrate_unit": "gh/s", "block_time": 60})

        return params

    @staticmethod
    def calculate_profitability(
        hash_rate: float,
        power_consumption: float,
        electricity_price_rub: float,
        coin_data: Dict[str, Dict],
        usd_to_rub: float,
        algorithm: str = "sha256",
        pool_fee: float = 0.0,  # Комиссия пула (например, 0.015 для 1.5%)
        electricity_price_usd: float = None  # Цена электроэнергии в USD (опционально)
    ) -> Dict[str, Any]:
        first_coin = list(coin_data.keys())[0]
        info = coin_data[first_coin]
        algorithm = info.get("algorithm", algorithm)

        algo_params = MiningCalculator.get_algorithm_params(algorithm)
        unit = algo_params["hashrate_unit"]

        # ========================================================================
        # ФОРМУЛА РАСЧЕТА ДОХОДА ПО ХЭШРЕЙТУ (на основе capminer.ru):
        # ========================================================================
        # 
        # ШАГ 1: Расчет доли майнера в сети
        #   share = miner_hashrate / network_hashrate
        #   ВАЖНО: единицы измерения должны совпадать!
        #   Для SHA-256: оба в TH/s
        #   Для Scrypt: оба в GH/s
        #   Для Etchash: оба в MH/s
        #   Для kHeavyHash: оба в TH/s
        #
        # ШАГ 2: Расчет количества блоков в день
        #   blocks_per_day = 86400 / block_time
        #   Для kHeavyHash: blocks_per_day = 86400 (1 блок в секунду)
        #   ВАЖНО: block_time может быть разным для разных монет одного алгоритма
        #   (например, LTC и DOGE оба Scrypt, но block_time разный: 150 и 60 сек)
        #
        # ШАГ 3: Расчет количества монет в день (БЕЗ комиссии пула)
        #   daily_coins_without_fee = share × blocks_per_day × block_reward
        #
        # ШАГ 4: Применение комиссии пула
        #   daily_coins = daily_coins_without_fee × (1 - pool_fee)
        #   Если pool_fee = 0.015 (1.5%), то daily_coins = daily_coins_without_fee × 0.985
        #
        # ШАГ 5: Расчет дохода в USD
        #   daily_income_usd = daily_coins × coin_price_usd
        #
        # ШАГ 6: Расчет дохода в RUB
        #   daily_income_rub = daily_income_usd × usd_to_rub
        #
        # ПРИМЕЧАНИЕ: efficiency_factor НЕ используется (capminer.ru его не применяет)
        # ========================================================================
        
        # ВАЖНО: Конвертируем единицы измерения для правильного расчета доли
        # hash_rate приходит в единицах, указанных в algo_params["hashrate_unit"]
        # network_hashrate в БД может быть в других единицах
        # Нужно привести к одинаковым единицам!
        
        # Определяем единицы для network_hashrate на основе алгоритма
        # Для SHA-256: оба в TH/s
        # Для Scrypt: оба в GH/s (network_hashrate в БД в GH/s)
        # Для Etchash: hash_rate приходит в GH/s (как на capminer.ru), network_hashrate в БД в MH/s
        # Для kHeavyHash: оба в TH/s
        
        miner_hash = hash_rate
        network_hash = info["network_hashrate"]
        
        # Конвертация единиц для правильного расчета доли майнера
        # ВАЖНО: hash_rate может приходить в разных единицах в зависимости от источника:
        # - Для ручного ввода: в единицах, указанных в algo_params["hashrate_unit"]
        # - Для ASIC-майнеров: может быть в других единицах
        # network_hashrate в БД хранится в определенных единицах для каждого алгоритма:
        # - SHA-256: TH/s
        # - Scrypt: GH/s
        # - Etchash: MH/s
        # - kHeavyHash: TH/s
        # - Blake2S: TH/s
        # Нужно привести miner_hash и network_hash к одинаковым единицам!
        
        algorithm_lower_check = algorithm.lower()
        
        if algorithm_lower_check in ["scrypt"]:
            # Для Scrypt:
            # - network_hashrate в БД: GH/s (например, 3,464,270 GH/s)
            # - hash_rate может быть в MH/s (L7: 8800 MH/s) или в GH/s (L9: 15 GH/s)
            # - Если hash_rate > 1000, вероятно это MH/s, конвертируем в GH/s
            # - Если hash_rate <= 1000, вероятно это уже GH/s
            if hash_rate > 1000:  # Если значение большое, вероятно это MH/s
                miner_hash = hash_rate / 1000  # MH/s -> GH/s
            else:
                miner_hash = hash_rate  # Уже в GH/s
            # network_hash уже в GH/s, не конвертируем
        
        elif algorithm_lower_check in ["etchash", "ethash", "etchash/ethash"]:
            # Для Etchash:
            # - network_hashrate в БД: MH/s (например, 387,376,804 MH/s)
            # - hash_rate может быть в MH/s (ASIC: 2400, 3280, 850, 950, 3000-3700 MH/s) или в GH/s (ручной ввод: GH/s)
            # - Для ASIC-майнеров: значения всегда >= 850 MH/s (850, 950, 2400, 3280, 3000-3700)
            # - Для ручного ввода: значения в GH/s (как на capminer.ru), обычно 1-1000 GH/s
            # - hashrate_unit для Etchash = "gh/s", значит для ручного ввода hash_rate в GH/s
            # - Логика: если hash_rate >= 850, это скорее всего MH/s (ASIC), иначе GH/s (ручной ввод)
            if hash_rate >= 850:  # ASIC-майнеры: значения всегда >= 850 MH/s
                miner_hash = hash_rate  # Уже в MH/s
            else:
                # Ручной ввод: значения в GH/s (согласно hashrate_unit)
                miner_hash = hash_rate * 1000  # GH/s -> MH/s
            # network_hash уже в MH/s, не конвертируем
        
        elif algorithm_lower_check in ["kheavyhash"]:
            # Для kHeavyHash:
            # - network_hashrate в БД: TH/s (например, 1,600,793 TH/s)
            # - hash_rate должен быть в TH/s (KAS: 20 TH/s, Ice River: 0.4 TH/s, 0.2 TH/s, 2 TH/s, 6 TH/s, 12 TH/s)
            # - Все значения уже в TH/s (KS0 ultra: 400 GH/s = 0.4 TH/s, KS0 PRO: 200 GH/s = 0.2 TH/s)
            # - Для ручного ввода пользователь вводит в TH/s (как указано в интерфейсе)
            miner_hash = hash_rate  # Уже в TH/s
            # network_hash уже в TH/s, не конвертируем
        
        else:
            # Для SHA-256, Blake2S и других:
            # - network_hashrate в БД: TH/s
            # - hash_rate должен быть в TH/s
            miner_hash = hash_rate  # Уже в TH/s
            # network_hash уже в TH/s, не конвертируем
        
        # ШАГ 1: Рассчитываем долю майнера (единицы должны совпадать!)
        share = miner_hash / network_hash if network_hash > 0 else 0

        # ШАГ 2: Блоков в день
        block_time = info.get("block_time", algo_params["block_time"])
        
        if algorithm.lower() == "kheavyhash":
            blocks_per_day = 86400  # 1 блок в секунду
        else:
            blocks_per_day = 86400 / block_time

        # ШАГ 3: Расчет количества монет в день (БЕЗ комиссии пула)
        daily_coins_without_fee = share * blocks_per_day * info["block_reward"]
        
        # ШАГ 4: Применяем комиссию пула (если указана)
        if pool_fee > 0:
            daily_coins = daily_coins_without_fee * (1 - pool_fee)
        else:
            daily_coins = daily_coins_without_fee
        
        # ШАГ 5 и 6: Расчет дохода
        daily_income_usd = daily_coins * info["price"]
        daily_income_rub = daily_income_usd * usd_to_rub
        
        # Расчет затрат на электроэнергию
        # Если указана цена в USD, используем её, иначе конвертируем из рублей
        if electricity_price_usd is not None:
            daily_electricity_cost_usd = (power_consumption / 1000) * 24 * electricity_price_usd
            daily_electricity_cost_rub = daily_electricity_cost_usd * usd_to_rub
        else:
            daily_electricity_cost_rub = (power_consumption / 1000) * 24 * electricity_price_rub
            daily_electricity_cost_usd = daily_electricity_cost_rub / usd_to_rub
        
        # Расчет прибыли
        daily_profit_usd = daily_income_usd - daily_electricity_cost_usd
        daily_profit_rub = daily_income_rub - daily_electricity_cost_rub

        def make_period(multiplier: int) -> Dict[str, Any]:
            coins_per_coin = {}
            # Используем daily_coins напрямую для всех монет (количество монет одинаково)
            # daily_coins уже рассчитано на основе доли майнера и награды за блок
            for symbol in coin_data.keys():
                coins = daily_coins * multiplier
                coins_per_coin[symbol] = coins
            return {
                "coins_per_coin": coins_per_coin,
                "income_usd": daily_income_usd * multiplier,
                "income_rub": daily_income_rub * multiplier,
                "electricity_cost_usd": daily_electricity_cost_usd * multiplier,
                "electricity_cost_rub": daily_electricity_cost_rub * multiplier,
                "profit_usd": daily_profit_usd * multiplier,
                "profit_rub": daily_profit_rub * multiplier,
            }

        return {
            "daily_income_usd": daily_income_usd,
            "daily_income_rub": daily_income_rub,
            "daily_electricity_cost_usd": daily_electricity_cost_usd,
            "daily_electricity_cost_rub": daily_electricity_cost_rub,
            "daily_profit_usd": daily_profit_usd,
            "daily_profit_rub": daily_profit_rub,
            "periods": {
                "day": make_period(1),
                "week": make_period(7),
                "month": make_period(30),
                "year": make_period(365),
            },
            "coin_data": coin_data,
            "original_hashrate": hash_rate,
            "hashrate_unit": unit,
            "power_consumption": power_consumption
        }

    @staticmethod
    def format_hashrate_display(hash_rate: float, unit: str) -> str:
        return f"{hash_rate} {unit.upper()}"

    @staticmethod
    def format_result(
        result: Dict[str, Any],
        coin_symbols: List[str],
        usd_to_rub: float,
    ) -> str:
        display_coins = coin_symbols[:5]
        hashrate_display = MiningCalculator.format_hashrate_display(
            result["original_hashrate"], result["hashrate_unit"]
        )

        text = ""
        text += f"💰 **Криптовалюта:** {', '.join(display_coins)}\n"
        
        text += f"🔌 **Потребление:** {result['power_consumption']:.1f}W\n\n"

        if not result["periods"]["day"]["coins_per_coin"]:
            text += "❌ Не удалось рассчитать доходность для указанных монет\n"
            return text

        text += "📊 **Доход в монетах:**\n"
        for period_name, period_display in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            coin_strings = []
            for symbol in display_coins:
                coins = result["periods"][period_name]["coins_per_coin"].get(symbol, 0)
                if coins == 0:
                    coin_strings.append(f"0.000000 {symbol}")
                elif symbol == "BTC":
                    coin_strings.append(f"{coins:.8f} {symbol}")
                elif coins < 0.001:
                    coin_strings.append(f"{coins:.6f} {symbol}")
                elif coins < 1:
                    coin_strings.append(f"{coins:.4f} {symbol}")
                else:
                    coin_strings.append(f"{coins:.2f} {symbol}")

            text += f"— За {period_display}: {' | '.join(coin_strings)}\n"

        text += "\n💵 **Доход в долларах:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["income_usd"]
            if val == 0:
                text += f"— За {name}: $0.00\n"
            elif val < 0.01:
                text += f"— За {name}: ${val:.4f}\n"
            elif val < 1:
                text += f"— За {name}: ${val:.3f}\n"
            else:
                text += f"— За {name}: ${val:.2f}\n"

        text += "\n⚡ **Затраты на электроэнергию:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["electricity_cost_usd"]
            text += f"— За {name}: ${val:.2f}\n"

        text += "\n📈 **Чистая доходность с учетом затрат на электроэнергию:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["profit_usd"]
            if val == 0:
                text += f"— За {name}: $0.00\n"
            elif abs(val) < 0.01:
                text += f"— За {name}: ${val:.4f}\n"
            elif abs(val) < 1:
                text += f"— За {name}: ${val:.3f}\n"
            else:
                text += f"— За {name}: ${val:.2f}\n"

        text += f"\n🕒 *Доходность актуальна на {datetime.now().strftime('%d.%m.%Y %H:%M')}*"

        return text

    @staticmethod
    def format_result_rub(
        result: Dict[str, Any], coin_symbols: List[str], usd_to_rub: float
    ) -> str:
        hashrate_display = MiningCalculator.format_hashrate_display(
            result["original_hashrate"], result["hashrate_unit"]
        )

        text = f"💰 **Результаты расчета в рублях**\n"
        
        text += f"🔌 **Потребление:** {result['power_consumption']:.1f}W\n\n"

        if not result["periods"]["day"]["income_rub"]:
            text += "❌ Не удалось рассчитать доходность\n"
            return text

        text += "💵 **Доход в рублях:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["income_rub"]
            if val == 0:
                text += f"— За {name}: 0.00 руб.\n"
            elif val < 0.01:
                text += f"— За {name}: {val:.4f} руб.\n"
            elif val < 1:
                text += f"— За {name}: {val:.3f} руб.\n"
            else:
                text += f"— За {name}: {val:.2f} руб.\n"

        text += "\n⚡ **Затраты на электроэнергию:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["electricity_cost_rub"]
            text += f"— За {name}: {val:.2f} руб.\n"

        text += "\n📈 **Чистая доходность:**\n"
        for period, name in [
            ("day", "день"),
            ("week", "неделю"),
            ("month", "месяц"),
            ("year", "год"),
        ]:
            val = result["periods"][period]["profit_rub"]
            if val == 0:
                text += f"— За {name}: 0.00 руб.\n"
            elif abs(val) < 0.01:
                text += f"— За {name}: {val:.4f} руб.\n"
            elif abs(val) < 1:
                text += f"— За {name}: {val:.3f} руб.\n"
            else:
                text += f"— За {name}: {val:.2f} руб.\n"

        text += f"\n🕒 *Актуально на {datetime.now().strftime('%d.%m.%Y %H:%M')}*"

        return text