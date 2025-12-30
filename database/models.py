# [file name]: models.py
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


class Manufacturer(str, Enum):
    BITMAIN = "Bitmain"
    WHATSMINER = "Whatsminer"
    ICERIVER = "Ice River"
    GOLDSHELL = "Goldshell"
    IPOLLO = "iPollo"
    OTHER = "Другой"


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


class AsicModelLine(Base):
    __tablename__ = "asic_model_lines"

    name = Column(String(100), nullable=False)
    manufacturer = Column(SQLEnum(Manufacturer), nullable=False)
    algorithm = Column(SQLEnum(Algorithm), nullable=False)

    models = relationship("AsicModel", back_populates="model_line")


class AsicModel(Base):
    __tablename__ = "asic_models"

    name = Column(String(100), nullable=False)
    model_line_id = Column(Integer, ForeignKey("asic_model_lines.id"))
    hash_rate = Column(Float, nullable=False)
    power_consumption = Column(Float, nullable=False)
    get_coin = Column(String(), default="")
    is_active = Column(Boolean, default=True)

    model_line = relationship("AsicModelLine", back_populates="models")
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
            print("[OK] Таблицы успешно созданы")

        async with self.async_session() as session:
            from sqlalchemy import select

            try:
                result = await session.execute(select(AlgorithmData))
                existing_data = result.scalars().first()
                
                if not existing_data:
                    print("[INFO] Добавляем начальные данные в algorithm_data...")
                    session.add_all(
                        [
                            AlgorithmData(
                                algorithm=Algorithm.SHA256,
                                default_coin="BTC",
                                difficulty=85_000_000_000_000_000,
                                network_hashrate=1_068_844_948,  # TH/s (≈ 1,068,845 PH/s) - актуальное значение для BTC
                                block_reward=3.125,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.KHEAVYHASH,
                                default_coin="KAS",
                                difficulty=150_000_000_000,
                                network_hashrate=1_600_793,  # TH/s - актуальное значение для KAS
                                block_reward=100,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.ETCHASH,
                                default_coin="ETC",
                                difficulty=50_000_000_000_000,
                                network_hashrate=387_376_804,  # MH/s (≈ 387,377 GH/s = 387 TH/s) - актуальное значение для ETC
                                block_reward=2.56,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.SCRYPT,
                                default_coin="LTC",
                                difficulty=15_000_000,
                                network_hashrate=2_684_855,  # GH/s (≈ 2,685 TH/s) - обновлено для соответствия capminer.ru
                                block_reward=6.25,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.BLAKE2S,
                                default_coin="KDA",  # KDA использует Blake2S
                                difficulty=200_000_000,
                                network_hashrate=86_853_786,  # TH/s - актуальное значение для KDA
                                block_reward=3.5,
                            ),
                            AlgorithmData(
                                algorithm=Algorithm.BLAKE2B_SHA3,
                                default_coin="KLS",
                                difficulty=3_000_000_000,
                                network_hashrate=200,
                                block_reward=12,
                            ),
                        ]
                    )
                    await session.commit()
                    print("[OK] Начальные данные algorithm_data добавлены")
                else:
                    print("[INFO] Данные в algorithm_data уже существуют")
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при работе с algorithm_data: {e}")
                await session.rollback()

            try:
                coins_exist = await session.execute(select(Coin))
                if not coins_exist.scalars().first():
                    print("[INFO] Добавляем начальные данные в coins...")
                    print("[INFO] Цены будут получены из API при инициализации")
                    # Монеты создаются без цен, цены будут получены из API через CoinGeckoService
                    session.add_all(
                        [
                            Coin(
                                symbol="BTC",
                                name="Bitcoin",
                                coin_gecko_id="bitcoin",
                                algorithm=Algorithm.SHA256,
                                current_price_usd=0.0,  # Будет обновлено из API
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="ETH",
                                name="Ethereum",
                                coin_gecko_id="ethereum",
                                algorithm=Algorithm.ETCHASH,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="LTC",
                                name="Litecoin",
                                coin_gecko_id="litecoin",
                                algorithm=Algorithm.SCRYPT,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="DOGE",
                                name="Dogecoin",
                                coin_gecko_id="dogecoin",
                                algorithm=Algorithm.SCRYPT,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="KAS",
                                name="Kaspa",
                                coin_gecko_id="kaspa",
                                algorithm=Algorithm.KHEAVYHASH,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="BCH",
                                name="Bitcoin Cash",
                                coin_gecko_id="bitcoin-cash",
                                algorithm=Algorithm.SHA256,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="BSV",
                                name="Bitcoin SV",
                                coin_gecko_id="bitcoin-sv",
                                algorithm=Algorithm.SHA256,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="ETC",
                                name="Ethereum Classic",
                                coin_gecko_id="ethereum-classic",
                                algorithm=Algorithm.ETCHASH,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="KDA",
                                name="Kadena",
                                coin_gecko_id="kadena",
                                algorithm=Algorithm.BLAKE2S,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                            Coin(
                                symbol="ETHW",
                                name="Ethereum PoW",
                                coin_gecko_id="ethereum-pow-iou",
                                algorithm=Algorithm.ETCHASH,
                                current_price_usd=0.0,
                                current_price_rub=0.0,
                            ),
                        ]
                    )
                    await session.commit()
                    print("[OK] Начальные данные coins добавлены (цены будут обновлены из API)")
                else:
                    print("[INFO] Данные в coins уже существуют")
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при работе с coins: {e}")
                await session.rollback()

        print("[OK] База данных успешно инициализирована!")