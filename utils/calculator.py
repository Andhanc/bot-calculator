# calculator.py
from datetime import datetime
from typing import Any, Dict, List


class MiningCalculator:
    @staticmethod
    def get_algorithm_params(algorithm: str) -> Dict[str, float]:
        params = {
            "block_time": 600,
            "difficulty_factor": 1.0,
            "efficiency_factor": 1.0,
            "hashrate_unit": "th/s"
        }

        algorithm_lower = algorithm.lower()

        if algorithm_lower in ["sha-256", "sha256"]:
            params.update({"hashrate_unit": "th/s", "block_time": 600})
        elif algorithm_lower in ["scrypt"]:
            params.update({"hashrate_unit": "mh/s", "block_time": 150})
        elif algorithm_lower in ["etchash", "ethash"]:
            params.update({"hashrate_unit": "mh/s", "block_time": 13})
        elif algorithm_lower in ["kheavyhash"]:
            params.update({"hashrate_unit": "gh/s", "block_time": 1})
        elif algorithm_lower in ["blake2s"]:
            params.update({"hashrate_unit": "gh/s", "block_time": 30})
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
        algorithm: str = "sha256"
    ) -> Dict[str, Any]:
        first_coin = list(coin_data.keys())[0]
        info = coin_data[first_coin]
        algorithm = info.get("algorithm", algorithm)

        algo_params = MiningCalculator.get_algorithm_params(algorithm)
        unit = algo_params["hashrate_unit"]

        # ✅ Теперь всё в родных единицах
        miner_hash = hash_rate
        network_hash = info["network_hashrate"]

        share = miner_hash / network_hash if network_hash > 0 else 0

        if algorithm.lower() == "kheavyhash":
            blocks_per_day = 86400
        else:
            blocks_per_day = 86400 / algo_params["block_time"]

        daily_coins = share * blocks_per_day * info["block_reward"]
        daily_coins *= algo_params["efficiency_factor"]

        daily_income_usd = daily_coins * info["price"]
        daily_income_rub = daily_income_usd * usd_to_rub
        daily_electricity_cost_rub = (power_consumption / 1000) * 24 * electricity_price_rub
        daily_electricity_cost_usd = daily_electricity_cost_rub / usd_to_rub
        daily_profit_usd = daily_income_usd - daily_electricity_cost_usd
        daily_profit_rub = daily_income_rub - daily_electricity_cost_rub

        def make_period(multiplier: int) -> Dict[str, Any]:
            coins_per_coin = {}
            for symbol, coin in coin_data.items():
                coins = (daily_income_usd / coin["price"]) * multiplier if coin["price"] > 0 else 0
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
        
        text += f"🔌 **Потребление:** {result['power_consumption']:.1f}W\n"
        text += f"🔄 **Курс доллара:** {usd_to_rub:.2f} RUB\n\n"

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