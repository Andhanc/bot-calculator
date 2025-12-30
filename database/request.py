import re
from asyncio import Lock
from datetime import datetime
from typing import Dict, List, Optional, Set

from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import (
    Algorithm,
    AlgorithmData,
    AsicModel,
    AsicModelLine,
    BroadcastMessage,
    Coin,
    Link,
    Manufacturer,
    SellRequest,
    UsedDeviceGuide,
    User,
    UserStatus,
)


class UserReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def user_exists(self, uid: int) -> bool:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(select(User).where(User.uid == uid))
            return res.scalar() is not None

    async def add_user(self, uid: int, uname: str) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                try:
                    new_user = User(uid=uid, uname=uname)
                    session.add(new_user)
                    await session.commit()
                    return True
                except IntegrityError:
                    await session.rollback()
                    return False

    async def is_admin(self, uid: int) -> bool:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(User).where(
                    and_(User.uid == uid, User.status == UserStatus.ADMIN)
                )
            )
            return res.scalar() is not None

    async def toggle_notifications(self, uid: int) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                res = await session.execute(select(User).where(User.uid == uid))
                user = res.scalar()
                if user:
                    user.notifications = not user.notifications
                    await session.commit()
                    return user.notifications
                return False

    async def get_user_notifications_status(self, uid: int) -> bool:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(User.notifications).where(User.uid == uid)
            )
            return res.scalar() or False

    async def get_all_users(self) -> List[User]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(select(User))
            return list(res.scalars().all())

    async def get_user_by_uid(self, uid: int) -> Optional[User]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(select(User).where(User.uid == uid))
            return res.scalar()


class CalculatorReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def get_manufacturers(self) -> List[Manufacturer]:
        # Чтение - блокировка не нужна
        return list(Manufacturer)

    async def get_model_lines_by_manufacturer(
        self, manufacturer: Manufacturer
    ) -> List[AsicModelLine]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                # Получаем только линейки, в которых есть хотя бы одна активная модель
                res = await session.execute(
                    select(AsicModelLine)
                    .join(AsicModel, AsicModelLine.id == AsicModel.model_line_id)
                    .where(
                        AsicModelLine.manufacturer == manufacturer,
                        AsicModel.is_active == True
                    )
                    .distinct()
                )
                lines = list(res.scalars().all())

                def natural_sort_key(text):
                    return [
                        int(part) if part.isdigit() else part.lower()
                        for part in re.split(r"(\d+)", text)
                    ]

                lines.sort(key=lambda x: natural_sort_key(x.name))
                return lines

    async def get_asic_models_by_model_line(
        self, model_line_id: int
    ) -> List[AsicModel]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModel)
                    .where(AsicModel.model_line_id == model_line_id)
                    .order_by(AsicModel.name)
                )
                return list(res.scalars().all())

    async def get_model_line_by_id(self, model_line_id: int) -> Optional[AsicModelLine]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModelLine).where(AsicModelLine.id == model_line_id)
                )
                return res.scalar()

    async def get_all_asic_models(self) -> List[AsicModel]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModel).where(AsicModel.is_active == True)
                )
                return list(res.scalars().all())

    async def get_asic_model_by_id(self, model_id: int) -> Optional[AsicModel]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModel).where(AsicModel.id == model_id)
                )
                return res.scalar()

    async def add_model_line(
        self,
        name: str,
        manufacturer: Manufacturer,
        algorithm: Algorithm,
    ) -> int:
        async with self.lock:
            async with self.db_session_maker() as session:
                model_line = AsicModelLine(
                    name=name,
                    manufacturer=manufacturer,
                    algorithm=algorithm,
                )
                session.add(model_line)
                await session.flush()
                model_line_id = model_line.id
                await session.commit()
                return model_line_id

    async def add_asic_model(
        self,
        name: str,
        model_line_id: int,
        hash_rate: float,
        power_consumption: float,
        get_coin: str = "",
    ) -> int:
        async with self.lock:
            async with self.db_session_maker() as session:
                model = AsicModel(
                    name=name,
                    model_line_id=model_line_id,
                    hash_rate=hash_rate,
                    power_consumption=power_consumption,
                    get_coin=get_coin,
                    is_active=True,
                )
                session.add(model)
                await session.flush()
                model_id = model.id
                await session.commit()
                return model_id

    async def delete_model_line(self, model_line_id: int) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModelLine).where(AsicModelLine.id == model_line_id)
                )
                model_line = res.scalar()
                if model_line:
                    await session.delete(model_line)
                    await session.commit()
                    return True
                return False

    async def delete_asic_model(self, model_id: int) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AsicModel).where(AsicModel.id == model_id)
                )
                model = res.scalar()
                if model:
                    await session.delete(model)
                    await session.commit()
                    return True
                return False

    async def get_algorithms(self) -> List[Algorithm]:
        # Чтение - блокировка не нужна
        return list(Algorithm)

    async def get_algorithm_data(self, algorithm: Algorithm) -> Optional[AlgorithmData]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AlgorithmData).where(AlgorithmData.algorithm == algorithm)
                )
                return res.scalar()

    async def get_algorithm_data_all(self) -> List[AlgorithmData]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(select(AlgorithmData))
            return list(res.scalars().all())
    
    async def get_algorithm_data_batch(self, algorithms: Set[Algorithm]) -> Dict[Algorithm, AlgorithmData]:
        """Получить данные алгоритмов одним запросом"""
        # Чтение - блокировка не нужна
        if not algorithms:
            return {}
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(AlgorithmData).where(AlgorithmData.algorithm.in_(algorithms))
            )
            algo_data_list = res.scalars().all()
            return {data.algorithm: data for data in algo_data_list}

    async def update_algorithm_data(
        self,
        algorithm: Algorithm,
        default_coin: str,
        difficulty: float,
        network_hashrate: float,
        block_reward: float,
    ) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                res = await session.execute(
                    select(AlgorithmData).where(AlgorithmData.algorithm == algorithm)
                )
                data = res.scalar()
                if data:
                    data.default_coin = default_coin
                    data.difficulty = difficulty
                    data.network_hashrate = network_hashrate
                    data.block_reward = block_reward
                    data.last_updated = datetime.now()
                else:
                    data = AlgorithmData(
                        algorithm=algorithm,
                        default_coin=default_coin,
                        difficulty=difficulty,
                        network_hashrate=network_hashrate,
                        block_reward=block_reward,
                    )
                    session.add(data)
                await session.commit()
                return True

    async def update_link(self, link: str) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                # Пытаемся найти существующую запись с ссылкой
                res = await session.execute(select(Link).order_by(Link.id.desc()))
                data = res.scalars().first()

                if data:
                    # Обновляем существующую ссылку
                    data.link = link
                else:
                    # Если записи нет — создаем новую
                    data = Link(link=link)
                    session.add(data)

                await session.commit()
                return True

    async def get_link(self) -> str:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
                # Берем последнюю (или единственную) запись из таблицы link
                res = await session.execute(select(Link).order_by(Link.id.desc()))
                data = res.scalars().first()

                # Если ссылки нет в базе – возвращаем None
                if not data:
                    return None

                return data.link

    async def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(Coin).where(Coin.symbol == symbol.upper())
            )
            return res.scalar()


class CoinReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def update_coin_prices(self, prices: Dict[str, Dict]) -> None:
        """Обновление цен монет с данными из CoinGecko"""
        async with self.lock:
            async with self.db_session_maker() as session:
                for symbol, price_data in prices.items():
                    res = await session.execute(
                        select(Coin).where(Coin.symbol == symbol.upper())
                    )
                    coin = res.scalar()
                    if coin:
                        coin.current_price_usd = price_data.get("price_usd", 0.0)
                        coin.current_price_rub = price_data.get("price_rub", 0.0)
                        coin.price_change_24h = price_data.get("price_change", 0.0)
                        coin.last_updated = datetime.now()
                await session.commit()

    async def get_all_coins(self) -> List[Coin]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(select(Coin))
            return list(res.scalars().all())

    async def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(Coin).where(Coin.symbol == symbol.upper())
            )
            return res.scalar()

    async def get_coin_by_gecko_id(self, gecko_id: str) -> Optional[Coin]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(Coin).where(Coin.coin_gecko_id == gecko_id.lower())
            )
            return res.scalar()
    
    async def get_coins_by_symbols(self, symbols: List[str]) -> Dict[str, Coin]:
        """Получить несколько монет одним запросом"""
        # Чтение - блокировка не нужна
        if not symbols:
            return {}
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(Coin).where(Coin.symbol.in_([s.upper() for s in symbols]))
            )
            coins = res.scalars().all()
            return {coin.symbol: coin for coin in coins}


class SellRequestReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def create_sell_request(
        self,
        user_id: int,
        device_id: int,
        price: float,
        condition: str,
        description: str,
        contact_info: str,
    ) -> int:
        async with self.lock:
            async with self.db_session_maker() as session:
                request = SellRequest(
                    user_id=user_id,
                    device_id=device_id,
                    price=price,
                    condition=condition,
                    description=description,
                    contact_info=contact_info,
                )
                session.add(request)
                await session.commit()
                return request.id

    async def get_pending_requests(self) -> List[SellRequest]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(SellRequest)
                .where(SellRequest.status == "pending")
                .order_by(SellRequest.created_at.desc())
            )
            return list(res.scalars().all())

    async def update_request_status(self, request_id: int, status: str) -> bool:
        async with self.lock:
            async with self.db_session_maker() as session:
                res = await session.execute(
                    select(SellRequest).where(SellRequest.id == request_id)
                )
                request = res.scalar()
                if request:
                    request.status = status
                    await session.commit()
                    return True
                return False


class BroadcastReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def save_broadcast(
        self, message_text: str, photo_url: str, sent_by: int
    ) -> int:
        async with self.lock:
            async with self.db_session_maker() as session:
                broadcast = BroadcastMessage(
                    message_text=message_text, photo_url=photo_url, sent_by=sent_by
                )
                session.add(broadcast)
                await session.commit()
                return broadcast.id


class UsedDeviceGuideReq:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker
        self.lock = Lock()

    async def get_guide(self) -> Optional[UsedDeviceGuide]:
        # Чтение - блокировка не нужна
        async with self.db_session_maker() as session:
            res = await session.execute(
                select(UsedDeviceGuide).order_by(
                    UsedDeviceGuide.last_updated.desc()
                )
            )
            return res.scalar()

    async def update_guide(self, title: str, content: str, updated_by: int) -> int:
        async with self.lock:
            async with self.db_session_maker() as session:
                guide = UsedDeviceGuide(
                    title=title, content=content, updated_by=updated_by
                )
                session.add(guide)
                await session.commit()
                return guide.id
