import asyncio
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from signature import Settings
from utils.coin_service import CoinGeckoService
from utils.logger import setup_logger


class BotRunner:
    def __init__(self):
        self.bot_instance = Settings()
        self.scheduler = AsyncIOScheduler()
        self.coin_service = CoinGeckoService(self.bot_instance)

    async def setup(self):
        await self.bot_instance.db_manager.async_main()
        await self.coin_service.initialize_coins()
        from handlers.admin import Admin
        from handlers.client import Client

        await setup_logger(level="DEBUG")
        user_client = Client(bot=self.bot_instance)
        admin_client = Admin(bot=self.bot_instance)
        await user_client.register_handlers()
        await admin_client.register_handler()
        self.setup_scheduler()

    def setup_scheduler(self):
        # Обновление цен и отправка курсов каждые 5 минут
        # Первое обновление произойдет сразу при старте (misfire_grace_time=None)
        trigger = IntervalTrigger(minutes=5)
        self.scheduler.add_job(
            self.coin_service.update_coin_prices_and_notify,
            trigger,
            id="price_update_interval",
            max_instances=1,  # Только один экземпляр задачи может выполняться одновременно
        )

    async def run(self):
        await self.setup()
        self.scheduler.start()
        print("Планировщик запущен. Цены и курсы будут обновляться каждые 5 минут")
        
        # Обновляем цены сразу при старте
        print("Первоначальное обновление цен...")
        try:
            await self.coin_service.update_coin_prices_and_notify()
        except Exception as e:
            print(f"Ошибка при первоначальном обновлении цен: {e}")
        
        # Останавливаем предыдущие webhook/polling соединения
        try:
            await self.bot_instance.bot.delete_webhook(drop_pending_updates=True)
            print("Предыдущие соединения закрыты")
        except Exception as e:
            print(f"Предупреждение при закрытии предыдущих соединений: {e}")
        
        try:
            await self.bot_instance.dp.start_polling(
                self.bot_instance.bot,
                drop_pending_updates=True
            )
        finally:
            await self.bot_instance.bot.session.close()
            self.scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(BotRunner().run())
    except KeyboardInterrupt:
        print("Bot stopped")
