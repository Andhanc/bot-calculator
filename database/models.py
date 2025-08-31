# database/models.py
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)


# --- ENUMS -------------------------------------------------------------


class UserStatus(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Algorithm(str, Enum):
    SHA256 = "SHA-256"
    SCRYPT = "Scrypt"
    ETCHASH = "Etchash/Ethash"
    KHEAVYHASH = "kHeavyHash"
    BLAKE2S = "Blake2S"
    BLAKE2B_SHA3 = "Blake2B+SHA3"
    EAGLESONG = "Eaglesong"
    CUCKAROO = "Cuckaroo"
    CUCKATOO = "Cuckatoo"


class Manufacturer(str, Enum):
    BITMAIN = "Bitmain"
    WHATSMINER = "Whatsminer"
    ICERIVER = "Ice River"
    GOLDSHELL = "Goldshell"
    IPOLLO = "iPollo"
    JASMINER = "JASMINER"
    ELPHAPEX = "Elphapex"
    BOMBAX = "Bombax"
    AVALON = "Avalon"
    OTHER = "Другой"


# --- TABLES ------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    uid = Column(BigInteger, nullable=False, unique=True)
    uname = Column(String(50))
    status = Column(SQLEnum(UserStatus), default=UserStatus.USER)
    notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    sell_requests = relationship("SellRequest", back_populates="user")


class Coin(Base):
    __tablename__ = "coins"

    symbol = Column(String(10), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    coin_gecko_id = Column(String(50), nullable=False)
    algorithm = Column(SQLEnum(Algorithm), nullable=False)
    current_price_usd = Column(Float, default=0.0)
    current_price_rub = Column(Float, default=0.0)
    price_change_24h = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.now())


class AsicModel(Base):
    __tablename__ = "asic_models"

    name = Column(String(100), nullable=False)
    manufacturer = Column(SQLEnum(Manufacturer), nullable=False)
    algorithm = Column(SQLEnum(Algorithm), nullable=False)
    hash_rate = Column(Float, nullable=False)
    power_consumption = Column(Float, nullable=False)
    price_usd = Column(Float, default=0.0)
    get_coin = Column(String(), default="")
    is_active = Column(Boolean, default=True)

    sell_requests = relationship("SellRequest", back_populates="device")


class AlgorithmData(Base):
    __tablename__ = "algorithm_data"

    algorithm = Column(SQLEnum(Algorithm), nullable=False, unique=True)
    default_coin = Column(String(10), nullable=False)
    difficulty = Column(Float, default=0.0)
    network_hashrate = Column(Float, default=0.0)
    block_reward = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.now)


class SellRequest(Base):
    __tablename__ = "sell_requests"

    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("asic_models.id"))
    price = Column(Float, nullable=False)
    condition = Column(String(20), nullable=False)
    description = Column(Text)
    contact_info = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="sell_requests")
    device = relationship("AsicModel", back_populates="sell_requests")


class BroadcastMessage(Base):
    __tablename__ = "broadcast_messages"

    message_text = Column(Text, nullable=False)
    photo_url = Column(String(255))
    sent_at = Column(DateTime, default=datetime.now)
    sent_by = Column(Integer, ForeignKey("users.id"))


class UsedDeviceGuide(Base):
    __tablename__ = "used_device_guide"

    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    last_updated = Column(DateTime, default=datetime.now)
    updated_by = Column(Integer, ForeignKey("users.id"))


class Link(Base):
    __tablename__ = "link"

    link = Column(String(), nullable=False)


# --- ENGINE & SESSION --------------------------------------------------


class CreateDatabase:
    def __init__(self, database_url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(url=database_url, echo=echo)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )

    @asynccontextmanager
    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def async_main(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Таблицы успешно созданы")

            # Начальные данные (при первом запуске)
            async with self.async_session() as session:
                from sqlalchemy import select

                if not await session.scalar(select(AlgorithmData)):
                    session.add_all(
                        [
                            AlgorithmData(
                                algorithm=Algorithm.SHA256,
                                default_coin="BTC",
                                difficulty=1e13,
                                network_hashrate=200_000_000,
                                block_reward=6.25,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.KHEAVYHASH,
                                default_coin="KAS",
                                difficulty=1.5e9,
                                network_hashrate=300,
                                block_reward=200,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.ETCHASH,
                                default_coin="ETC",
                                difficulty=5e11,
                                network_hashrate=50_000,
                                block_reward=2.56,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.BLAKE2S,
                                default_coin="NEOX",
                                difficulty=1.5e8,
                                network_hashrate=2_500,
                                block_reward=4.5,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.BLAKE2B_SHA3,
                                default_coin="KLS",
                                difficulty=2e9,
                                network_hashrate=150,
                                block_reward=15,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.EAGLESONG,
                                default_coin="CKB",
                                difficulty=8e10,
                                network_hashrate=180_000,
                                block_reward=1_917,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.CUCKAROO,
                                default_coin="GRIN",
                                difficulty=2e9,
                                network_hashrate=5,
                                block_reward=60,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.CUCKATOO,
                                default_coin="GRIN",
                                difficulty=1e10,
                                network_hashrate=8,
                                block_reward=60,
                            ),
                        ]
                    )
                    await session.commit()
                coins_exist = await session.execute(select(Coin))
                if not coins_exist.scalars().first():
                    session.add_all(
                        [
                            Coin(
                                symbol="BTC",
                                name="Bitcoin",
                                coin_gecko_id="bitcoin",  # Добавьте это поле!
                                algorithm=Algorithm.SHA256,
                                current_price_usd=45000.0,
                                current_price_rub=45000.0 * 90,  # Пример конвертации
                            ),
                            Coin(
                                symbol="KAS",
                                name="Kaspa",
                                coin_gecko_id="kaspa",  # Добавьте это поле!
                                algorithm=Algorithm.KHEAVYHASH,
                                current_price_usd=0.087,
                                current_price_rub=0.087 * 90,
                            ),
                            Coin(
                                symbol="ETC",
                                name="Ethereum Classic",
                                coin_gecko_id="ethereum-classic",  # Добавьте это поле!
                                algorithm=Algorithm.ETCHASH,
                                current_price_usd=21.67,
                                current_price_rub=21.67 * 90,
                            ),
                            Coin(
                                symbol="USDT",
                                name="Tether",
                                coin_gecko_id="tether",  # Добавьте это поле!
                                algorithm=Algorithm.EAGLESONG,  # У USDT нет алгоритма
                                current_price_usd=1.0,  # USDT ≈ $1
                                current_price_rub=80.70,  # Ты указал актуальную цену
                            ),
                            Coin(
                                symbol="DOGE",
                                name="Dogecoin",
                                coin_gecko_id="dogecoin",  # Добавьте это поле!
                                algorithm=Algorithm.SCRYPT,
                                current_price_usd=0.23,
                                current_price_rub=0.23 * 90,
                            ),
                            Coin(
                                symbol="LTC",
                                name="Litecoin",
                                coin_gecko_id="litecoin",  # Добавьте это поле!
                                algorithm=Algorithm.SCRYPT,
                                current_price_usd=120.02,
                                current_price_rub=120.02 * 90,
                            ),
                        ]
                    )
                    await session.commit()
