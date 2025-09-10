import asyncio
import logging
from typing import Dict, List

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import Coin
from database.request import CoinReq, UserReq
from signature import Settings

logger = logging.getLogger(__name__)


class CoinGeckoService:
    def __init__(self, settings: Settings):
        self.db_session_maker = settings.db_manager.async_session
        self.coin_req = CoinReq(settings.db_manager.async_session)
        self.user_req = UserReq(settings.db_manager.async_session)
        self.base_url = "https://api.coingecko.com/api/v3"
        self.coin_mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDT": "tether",
            "DOGE": "dogecoin",
            "LTC": "litecoin",
            "KAS": "kaspa",
        }
        self.bot = settings.bot

    async def fetch_prices(self) -> Dict[str, Dict]:
        try:
            coin_ids = ",".join(self.coin_mapping.values())
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/simple/price",
                    params={
                        "ids": coin_ids,
                        "vs_currencies": "usd,rub",
                        "include_24hr_change": "true",
                    },
                    timeout=30,
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Ошибка при получении цен с CoinGecko: {e}")
            return {}

    async def update_coin_prices_and_notify(self):
        try:
            prices = await self.fetch_prices()
            if not prices:
                logger.warning("Не удалось получить цены с CoinGecko")
                return

            update_data = {}
            for symbol, coin_gecko_id in self.coin_mapping.items():
                if coin_gecko_id in prices:
                    coin_data = prices[coin_gecko_id]
                    update_data[symbol] = {
                        "price_usd": coin_data.get("usd", 0.0),
                        "price_rub": coin_data.get("rub", 0.0),
                        "price_change": coin_data.get("usd_24h_change", 0.0),
                    }

            await self.coin_req.update_coin_prices(update_data)
            logger.info(f"Цены обновлены для {len(update_data)} монет")
            await self.send_price_notification(update_data)
        except Exception as e:
            logger.error(f"Ошибка при обновлении цен: {e}")

    async def send_price_notification(self, prices_data: Dict[str, Dict]):
        try:
            coins = await self.coin_req.get_all_coins()

            target_symbols = ["BTC", "ETH", "LTC", "DOGE", "KAS"]
            filtered_coins = [coin for coin in coins if coin.symbol in target_symbols]

            message = "💰 *Обновление цен монет*\n\n"

            for coin in filtered_coins:
                if coin.symbol in prices_data:
                    data = prices_data[coin.symbol]
                    change_icon = "📈" if data["price_change"] >= 0 else "📉"
                    message += (
                        f"🔸 *{coin.symbol}* ({coin.name})\n"
                        f"   💵 ${data['price_usd']:,.2f} | ₽{data['price_rub']:,.0f}\n"
                        f"   {change_icon} {data['price_change']:+.1f}%\n\n"
                    )

            users = await self.user_req.get_all_users()
            for user in users:
                if user.notifications:
                    try:
                        await self.bot.send_message(
                            user.uid, message, parse_mode="Markdown"
                        )
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(
                            f"Не удалось отправить уведомление пользователю {user.uid}: {e}"
                        )
            await self.bot.send_message(-1001546174824, message, parse_mode="Markdown")
            logger.info(f"Уведомления отправлены {len(users)} пользователям")

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомлений: {e}")

    async def get_usd_rub_rate(self) -> float:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/simple/price",
                    params={"ids": "tether", "vs_currencies": "rub"},
                    timeout=10,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("tether", {}).get("rub", 80.0)
        except Exception as e:
            logger.error(f"Ошибка при получении курса USD/RUB: {e}")
            return 80.0

    async def initialize_coins(self):
        async with self.db_session_maker() as session:
            from sqlalchemy import select

            existing_coins = await session.execute(select(Coin))
            if not existing_coins.scalars().first():
                coins_to_add = [
                    {
                        "symbol": "BTC",
                        "name": "Bitcoin",
                        "coin_gecko_id": "bitcoin",
                        "algorithm": "SHA256",
                        "current_price_usd": 45000.0,
                        "current_price_rub": 3600000.0,
                        "price_change_24h": 0.0,
                    },
                    {
                        "symbol": "ETH",
                        "name": "Ethereum",
                        "coin_gecko_id": "ethereum",
                        "algorithm": "ETCHASH",
                        "current_price_usd": 4397,
                        "current_price_rub": 430000.0,
                        "price_change_24h": 0.0,
                    },
                    {
                        "symbol": "KAS",
                        "name": "Kaspa",
                        "coin_gecko_id": "kaspa",
                        "algorithm": "KHEAVYHASH",
                        "current_price_usd": 0.087,
                        "current_price_rub": 7.0,
                        "price_change_24h": 0.0,
                    },
                    {
                        "symbol": "LTC",
                        "name": "Litecoin",
                        "coin_gecko_id": "litecoin",
                        "algorithm": "SCRYPT",
                        "current_price_usd": 75.0,
                        "current_price_rub": 6000.0,
                        "price_change_24h": 0.0,
                    },
                    {
                        "symbol": "DOGE",
                        "name": "Dogecoin",
                        "coin_gecko_id": "dogecoin",
                        "algorithm": "SCRYPT",
                        "current_price_usd": 0.15,
                        "current_price_rub": 12.0,
                        "price_change_24h": 0.0,
                    },
                ]
                for coin_data in coins_to_add:
                    coin = Coin(**coin_data)
                    session.add(coin)
                await session.commit()
                logger.info("Монеты инициализированы")
