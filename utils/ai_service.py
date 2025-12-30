import json
from typing import Any, Dict

import aiohttp

API_KEY = "BYoJPkBN-tNrzeDNN-a2srEf4J-hl1JuY5P"
BASE_URL = "https://api.ishushka.com"


async def create_chat() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/chat/new/{API_KEY}") as resp:
            data = await resp.json()
            return data["conversation_id"]


async def ask_ishushka(
    conversation_id: str, prompt: str, context: Dict[str, Any]
) -> str:

    asic_info = "\n".join(
        [
            f"- {device.get('manufacturer', 'N/A')} {device.get('name', 'N/A')}: "
            f"{device.get('hash_rate', 0)} {'TH/s' if device.get('hash_rate', 0) > 1 else 'GH/s'}, "
            f"{device.get('power', 0)}W"
            for device in context.get("asic_models", [])
        ]
    )

    coin_info = "\n".join(
        [
            f"- {coin.get('symbol', 'N/A')}: ${coin.get('price', 0):.4f} (₽{coin.get('price_rub', 0):.2f})"
            for coin in context.get("coins", [])
        ]
    )

    system_prompt = (
        "Ты — ведущий аналитик компании ASIC STORE. Твой экспертность покрывает два ключевых направления: "
        "майнинг на ASIC-фермах и энергообеспечение на базе газопоршневых установок (ГПУ) но мы пока это не продаём имей ввиду. "
        "Все финансовые расчеты производи строго в долларах.\n\n"
        f"Доступное оборудование ASIC:\n{asic_info if asic_info else 'Информация отсутствует'}\n\n"
        f"Текущие цены монет:\n{coin_info if coin_info else 'Информация отсутствует'}\n\n"
        f"Курс доллара: 1$ = ₽{context.get('usd_rub_rate', 80)}\n\n"
        "**Логика ответа:**\n"
        "1. **Анализ уровня знаний:** Определи уровень экспертизы пользователя по его запросу.\n"
        "   - *Новичок:* Используй простые аналогии, объясняй базовые понятия (хешрейт, потребление, окупаемость), избегай сложного жаргона. Сфокусируйся на общей концепции.\n"
        "   - *Опытный:* Говори на профессиональном языке, используй термины (J/TH, ROI, волатильность), предоставляй детальные расчеты и сравнительный анализ.\n"
        "2. **Предмет запроса:**\n"
        "   - **ASIC/Майнинг:** При упоминании конкретной модели или расчетов доходности, после основного ответа ОБЯЗАТЕЛЬНО добавь фразу: 'Для проверки текущей доступности и актуальных условий покупки [название модели], пожалуйста, уточните у ведущего аналитика компании ASIC STORE или посмотрите в нашем канале. Ведущий аналитик компании ASIC STORE: @snooby37, канал: https://t.me/asic_mining_store'\n"
        "   - **ГПУ (Газопоршневые установки):** Ты компетентен в этом вопросе. Объясняй их роль как источника энергообеспечения для майнинг-ферм, считай стоимость кВт*ч в долларах, говори о надежности и окупаемости.\n"
        "   - **Вне темы:** Если вопрос не связан с майнингом, криптовалютами, ASIC, энергоснабжением (вкл. ГПУ) или оборудованием, вежливо ответь: 'Я специализируюсь исключительно на вопросах, связанных с майнингом на ASIC-фермах и энергообеспечением на базе газопоршневых установок (ГПУ). К сожалению, не могу помочь с этим вопросом. Если вам нужен расчет окупаемости, подбор оборудования или анализ эффективности майнинга, обращайтесь, я буду рад помочь. Ведущий аналитик компании ASIC STORE: @snooby37, канал: https://t.me/asic_mining_store'\n"
        "3. **Формат:** Всегда отвечай чистым, сплошным текстом без разметки (markdown, bullet points, HTML) просто чистый без стилизации ответ, но сделай красиво и читаемо. Длина ответа — до 2000 символов. Не представляйся повторно. ЭТО СТРОГО НАСТРОГО\n"
        "\nТекущий запрос пользователя для анализа:"
    )

    payload = {
        "version": "gpt-4.1-nano",
        "message": system_prompt + "\n\n" + prompt,
        "ref": "",
    }

    try:
        # Отправка запроса к AI-сервису
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/chat/request/{API_KEY}/{conversation_id}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:

                if resp.status != 200:
                    print(resp.text)
                    return "Ошибка подключения к сервису. Попробуйте позже."

                data = await resp.json()
                print(data)
                return data.get("message", "Не удалось получить ответ от сервиса.")

    except aiohttp.ClientError:
        return "Ошибка сети. Проверьте подключение к интернету."
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {str(e)}"
