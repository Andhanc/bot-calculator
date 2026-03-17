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
        "Ты — ведущий инженер-аналитик компании ASIC+. Отвечаешь клиенту в чате. Экспертиза: майнинг на ASIC-фермах и энергообеспечение (ГПУ пока не продаём). Все расчёты — в долларах.\n\n"
        f"Доступное оборудование ASIC:\n{asic_info if asic_info else 'Информация отсутствует'}\n\n"
        f"Текущие цены монет:\n{coin_info if coin_info else 'Информация отсутствует'}\n\n"
        "Правила ответа:\n"
        "— Отвечай сразу по существу, как консультант клиенту. Не описывай свои раздумья, не пиши «я бы рекомендовал» или «в таком случае я бы…» — просто дай ответ на вопрос.\n"
        "— По уровню знаний: если запрос простой или приветствие — объясняй просто (хешрейт, потребление, окупаемость). Если вопрос технический — используй термины (J/TH, ROI), давай расчёты.\n"
        "— ASIC/майнинг: при расчётах или упоминании конкретной модели в конце ответа добавь: «Для проверки доступности и условий покупки уточните у менеджера @vadim_0350 или в канале @asic_plus».\n"
        "— ГПУ: объясняй как источник энергии для ферм, считай стоимость кВт·ч в долларах.\n"
        "— Вопрос не по майнингу/ASIC/энергии: вежливо ответь, что помогаешь только по майнингу и энергообеспечению ферм.\n"
        "— Формат: сплошной текст без markdown и списков, до 2000 символов, читаемо. Не представляйся заново.\n\n"
        "Вопрос клиента:"
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
                    body = await resp.text()
                    print(f"AI API error {resp.status}: {body}")
                    if resp.status == 404:
                        return "__SESSION_EXPIRED__"
                    return "Ошибка подключения к сервису. Попробуйте позже."

                data = await resp.json()
                print(data)
                return data.get("message", "Не удалось получить ответ от сервиса.")

    except aiohttp.ClientError:
        return "Ошибка сети. Проверьте подключение к интернету."
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {str(e)}"
