from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ClientKB:
    @staticmethod
    async def back_ai() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def back_calc() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="calc_income")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🧮 Калькулятор", callback_data="calc_income")
        builder.button(text="🤖 AI-консультант", callback_data="ai_consult")
        builder.button(text="📋 Прайс-лист", callback_data="price_list")
        builder.button(text="🛠️ Ремонт ASIC+", callback_data="document")
        builder.button(text="📞 Связаться с менеджером", url="https://t.me/vadim_0350")
        builder.button(text="👤 Профиль", callback_data="profile")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def calc_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🧮 Калькулятор", callback_data="calc_calc")
        builder.button(text="📊 Характеристики", callback_data="calc_chars")
        builder.button(text="💎 Цены монет", callback_data="calc_coins")
        builder.button(text="🔙 Назад", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def confirm_a() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Отправить", callback_data="send_bp")
        builder.button(text="В меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def profile_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Хочу другую цену", callback_data="better_price")
        builder.button(text="📦 Продать оборудование", callback_data="sell_device")
        builder.button(text="📢 Перейти в канал", url="https://t.me/asic_plus")
        builder.button(text="📞 Связаться с менеджером", url="https://t.me/vadim_0350")
        builder.button(text="🔙 Назад", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def chars_manufacturer() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Bitmain", callback_data="chars_manufacturer:Bitmain")
        builder.button(text="Whatsminer", callback_data="chars_manufacturer:Whatsminer")
        builder.button(text="Ice River", callback_data="chars_manufacturer:Ice River")
        builder.button(text="Goldshell", callback_data="chars_manufacturer:Goldshell")
        builder.button(text="iPollo", callback_data="chars_manufacturer:iPollo")
        builder.button(text="🔙 Назад", callback_data="calc_income")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def chars_model_lines(model_lines: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for line in model_lines:
            builder.button(text=line.name, callback_data=f"chars_line:{line.id}")
        builder.button(text="🔙 Назад", callback_data="calc_chars")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def chars_models(models: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for model in models:
            builder.button(text=model.name, callback_data=f"chars_model:{model.id}")
        builder.button(text="🔙 Назад к линейкам", callback_data="back_chars_lines")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def chars_back() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад к моделям", callback_data="back_chars_models")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()
