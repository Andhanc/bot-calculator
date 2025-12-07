"""
Скрипт для заполнения базы данных ASIC-майнерами из SQL-скрипта
"""
import asyncio
from database.models import (
    CreateDatabase,
    AsicModelLine,
    AsicModel,
    Algorithm,
    Manufacturer,
)
from config import get_db_url
from sqlalchemy import select


async def fill_asic_models():
    """Заполнение базы данных ASIC-майнерами"""
    db_manager = CreateDatabase(database_url=get_db_url())
    await db_manager.async_main()
    
    async with db_manager.async_session() as session:
        # BITMAIN - S19
        s19_line = await get_or_create_model_line(
            session, "S19", Manufacturer.BITMAIN, Algorithm.SHA256
        )
        s19_models = [
            ("Bitmain Antminer S19 82 TH/s", 82, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 86 TH/s", 86, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 86 TH/s 126 Chip", 86, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 90 TH/s", 90, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 90 TH/s 126 Chip", 90, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 95 TH/s", 95, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 Pro 86 TH/s", 86, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 PRO 104 TH/s", 104, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 PRO 110TH/s", 110, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 PRO+ Hydro 184 TH/s", 184, 5060, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 PRO+ Hydro 198 TH/s", 198, 5440, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19K PRO 110 TH/s", 110, 3000, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19K PRO 115 TH/s", 115, 3000, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19K PRO 120 TH/s", 120, 3000, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19K PRO 136 TH/s", 136, 3050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 JXP 143 TH/s", 143, 3050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 XP 141 TH/s", 141, 3050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 XP 134 TH/s", 134, 3050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 JXP 151 TH/s", 151, 3050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19 XP Hydro 257 TH/s", 257, 5300, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19J PRO 100 TH/s", 100, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19J PRO 104 TH/s", 104, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19J PRO+ 117 TH/S", 117, 3350, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19J PRO+ 120 TH/S", 120, 3355, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S19J PRO+ 122 TH/S", 122, 3355, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
        ]
        await add_models(session, s19_line.id, s19_models)
        
        # BITMAIN - S21
        s21_line = await get_or_create_model_line(
            session, "S21", Manufacturer.BITMAIN, Algorithm.SHA256
        )
        s21_models = [
            ("Bitmain Antminer S21 200TH/s", 200, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 188 TH/s", 188, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 195 TH/s", 195, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21+ 216 TH/s", 216, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 Pro 220 TH/s", 220, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 Pro 234 TH/s", 234, 3500, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 XP 270 TH/s", 270, 3650, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 Hydro 319 Th/s", 319, 5360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 Hydro 335 Th/s", 335, 5360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 XP Hydro 473 Th/s", 473, 5680, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 XP IMM 300 Th/s", 300, 4050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer S21 IMM 239 Th/s", 239, 4050, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer U3S21EXPH 860 Th/s", 860, 11200, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
        ]
        await add_models(session, s21_line.id, s21_models)
        
        # BITMAIN - T21
        t21_line = await get_or_create_model_line(
            session, "T21", Manufacturer.BITMAIN, Algorithm.SHA256
        )
        t21_models = [
            ("Bitmain Antminer T21 180 TH/s", 180, 3610, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer T21 186 TH/s", 186, 3610, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Bitmain Antminer T21 190 TH/s", 190, 3610, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
        ]
        await add_models(session, t21_line.id, t21_models)
        
        # BITMAIN - L7 (Scrypt)
        l7_line = await get_or_create_model_line(
            session, "L7", Manufacturer.BITMAIN, Algorithm.SCRYPT
        )
        l7_models = [
            ("Bitmain Antminer L7 8800 MH/s", 8800, 3172, "LTC, DOGE"),
            ("Bitmain Antminer L7 8550 MH/s", 8550, 3300, "LTC, DOGE"),
            ("Bitmain Antminer L7 9050MH/s", 9050, 3260, "LTC, DOGE"),
            ("Bitmain Antminer L7 9300 MH/s", 9300, 3350, "LTC, DOGE"),
            ("Bitmain Antminer L7 9500 MH/s", 9500, 3420, "LTC, DOGE"),
        ]
        await add_models(session, l7_line.id, l7_models)
        
        # BITMAIN - L9 (Scrypt)
        l9_line = await get_or_create_model_line(
            session, "L9", Manufacturer.BITMAIN, Algorithm.SCRYPT
        )
        l9_models = [
            # L9 указан в GH/s, но network_hashrate для Scrypt в БД в GH/s
            # Храним в GH/s для правильного расчета
            ("Bitmain Antminer L9 15 GH/s", 15, 3260, "LTC, DOGE"),
            ("Bitmain Antminer L9 16 GH/s", 16, 3260, "LTC, DOGE"),
            ("Bitmain Antminer L9 17 GH/s", 17, 3260, "LTC, DOGE"),
            ("Bitmain Antminer L9 17,6 GH/s", 17.6, 3260, "LTC, DOGE"),
        ]
        await add_models(session, l9_line.id, l9_models)
        
        # BITMAIN - E9 (Etchash)
        e9_line = await get_or_create_model_line(
            session, "E9", Manufacturer.BITMAIN, Algorithm.ETCHASH
        )
        e9_models = [
            ("Bitmain Antminer E9 2400 MH/s", 2400, 2500, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3280 MH/s", 3280, 2200, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3380 MH/s", 3380, 2200, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3480 MH/s", 3480, 2200, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3580 MH/s", 3580, 2200, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3680 MH/s", 3680, 2200, "ETC, ETHW"),
            ("Bitmain Antminer E9 Pro 3780 MH/s", 3780, 2200, "ETC, ETHW"),
        ]
        await add_models(session, e9_line.id, e9_models)
        
        # BITMAIN - KA3 (Blake2S)
        ka3_line = await get_or_create_model_line(
            session, "KA3", Manufacturer.BITMAIN, Algorithm.BLAKE2S
        )
        ka3_models = [
            ("Bitmain Antminer KA3 173 TH/s", 173, 3154, "KDA"),
        ]
        await add_models(session, ka3_line.id, ka3_models)
        
        # BITMAIN - KAS (kHeavyHash)
        kas_line = await get_or_create_model_line(
            session, "KAS", Manufacturer.BITMAIN, Algorithm.KHEAVYHASH
        )
        kas_models = [
            ("Bitmain Antminer KAS Miner KS5", 20, 3150, "KASPA"),
            ("Bitmain Antminer KAS Miner KS5 Pro", 21, 3150, "KASPA"),
        ]
        await add_models(session, kas_line.id, kas_models)
        
        # WHATSMINER - M50
        m50_line = await get_or_create_model_line(
            session, "M50", Manufacturer.WHATSMINER, Algorithm.SHA256
        )
        m50_models = [
            ("Whatsminer M50S 126 TH/s", 126, 3480, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S 128 TH/s", 128, 3380, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S 130 TH/s", 130, 3380, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S 250 TH/s", 250, 6750, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50 114 Th/s", 114, 3360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50 116 TH/s", 116, 3360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50 118 TH/s", 118, 3360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50 120 TH/s", 120, 3480, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50 122 TH/s", 122, 3480, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S++ 150 TH/s", 150, 3432, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S++ 140 TH/s", 140, 3360, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S++ 138 TH/s", 138, 3312, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M50S++ 136 TH/s", 136, 3264, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M53 230 TH/s", 230, 6820, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M56S 200 TH/s", 200, 6572, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M53S++ 320 TH/s", 320, 7040, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
        ]
        await add_models(session, m50_line.id, m50_models)
        
        # WHATSMINER - M30
        m30_line = await get_or_create_model_line(
            session, "M30", Manufacturer.WHATSMINER, Algorithm.SHA256
        )
        m30_models = [
            ("Whatsminer M30S 100 TH/s", 100, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M30S 102 TH/s", 102, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M30S 104 TH/s", 104, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M30S 106 TH/s", 106, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M30S 108 TH/s", 108, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M30S 110 TH/s", 110, 3400, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M33S 216 TH/s", 216, 3900, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M36S 172 TH/s", 172, 3420, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M36S 238 TH/s", 238, 3420, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M60 166 TH/s", 166, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
            ("Whatsminer M60 176 TH/s", 176, 3250, "BTC, BCH, BSV, LCC, TRC, XJO, ACOIN, PPC, UNB, CRW, CURE"),
        ]
        await add_models(session, m30_line.id, m30_models)
        
        # ICERIVER - Ice River (kHeavyHash)
        iceriver_line = await get_or_create_model_line(
            session, "Ice River", Manufacturer.ICERIVER, Algorithm.KHEAVYHASH
        )
        iceriver_models = [
            ("IceRiver KS0 ultra", 400, 100, "KASPA"),
            ("ICERIVER KAS KS0 PRO", 200, 100, "KASPA"),
            ("Iceriver KS2 Lite", 2, 500, "KASPA"),
            ("ICERIVER KS3M", 6, 3200, "KASPA"),
            ("ICERIVER KS5L", 12, 3400, "KASPA"),
        ]
        await add_models(session, iceriver_line.id, iceriver_models)
        
        # GOLDSHELL - Goldshell (разные алгоритмы, используем SHA256 как временное)
        goldshell_line = await get_or_create_model_line(
            session, "Goldshell", Manufacturer.GOLDSHELL, Algorithm.SHA256
        )
        goldshell_models = [
            ("Goldshell E-DG1M", 3400, 1800, "Various"),
            ("Goldshell E-KA1M", 5.5, 1800, "Various"),
            ("Goldshell KA BOX 1.18TH", 1.18, 400, "Various"),
            ("Goldshell AL BOX 360G", 360, 240, "Various"),
        ]
        await add_models(session, goldshell_line.id, goldshell_models)
        
        # IPOLLO - iPollo (Etchash)
        ipollo_line = await get_or_create_model_line(
            session, "iPollo", Manufacturer.IPOLLO, Algorithm.ETCHASH
        )
        ipollo_models = [
            ("iPollo V1H 850mh", 850, 690, "ETC, ETH"),
            ("iPollo V1H 950mh", 950, 690, "ETC, ETH"),
            ("iPollo V2H 3000 MH/s", 3000, 475, "ETC, ETH"),
            ("iPollo V2H 3100 MH/s", 3100, 475, "ETC, ETH"),
            ("iPollo V2H 3200 MH/s", 3200, 475, "ETC, ETH"),
            ("iPollo V2H 3300 MH/s", 3300, 475, "ETC, ETH"),
            ("iPollo V2H 3400 MH/s", 3400, 475, "ETC, ETH"),
            ("iPollo V2H 3500 MH/s", 3500, 475, "ETC, ETH"),
            ("iPollo V2H 3600 MH/s", 3600, 475, "ETC, ETH"),
            ("iPollo V2H 3700 MH/s", 3700, 475, "ETC, ETH"),
            ("iPollo V2X 1200 MH/s", 1200, 475, "ETC, ETH"),
        ]
        await add_models(session, ipollo_line.id, ipollo_models)
        
        await session.commit()
        print("База данных успешно заполнена ASIC-майнерами!")


async def get_or_create_model_line(session, name: str, manufacturer: Manufacturer, algorithm: Algorithm):
    """Получить или создать линию моделей"""
    result = await session.execute(
        select(AsicModelLine).where(
            AsicModelLine.name == name,
            AsicModelLine.manufacturer == manufacturer,
            AsicModelLine.algorithm == algorithm,
        )
    )
    model_line = result.scalar_one_or_none()
    
    if not model_line:
        model_line = AsicModelLine(
            name=name,
            manufacturer=manufacturer,
            algorithm=algorithm,
        )
        session.add(model_line)
        await session.flush()
        print(f"Создана линия моделей: {name} ({manufacturer.value}, {algorithm.value})")
    else:
        print(f"Линия моделей уже существует: {name} ({manufacturer.value}, {algorithm.value})")
    
    return model_line


async def add_models(session, model_line_id: int, models: list):
    """Добавить модели майнеров"""
    added_count = 0
    skipped_count = 0
    
    for name, hash_rate, power_consumption, get_coin in models:
        # Проверяем, существует ли уже такая модель
        result = await session.execute(
            select(AsicModel).where(
                AsicModel.name == name,
                AsicModel.model_line_id == model_line_id,
            )
        )
        existing_model = result.scalar_one_or_none()
        
        if not existing_model:
            model = AsicModel(
                name=name,
                model_line_id=model_line_id,
                hash_rate=hash_rate,
                power_consumption=power_consumption,
                get_coin=get_coin,
                is_active=True,
            )
            session.add(model)
            added_count += 1
        else:
            skipped_count += 1
    
    await session.flush()
    print(f"  Добавлено моделей: {added_count}, пропущено (уже существуют): {skipped_count}")


if __name__ == "__main__":
    asyncio.run(fill_asic_models())

