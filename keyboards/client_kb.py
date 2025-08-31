from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ClientKB:
    @staticmethod
    async def back_ai() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="back_main")
        return builder.as_markup()

    @staticmethod
    async def back_calc() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="calc_income")
        return builder.as_markup()

    @staticmethod
    async def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Рассчитать доходность", callback_data="calc_income")
        builder.button(text="📋 Прайс-лист", callback_data="price_list")
        builder.button(text="👤 Профиль", callback_data="profile")
        builder.button(text="🤖 AI-консультант", callback_data="ai_consult")
        builder.button(
            text="📞 Связаться с менеджером", url="https://t.me/your_manager"
        )
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
    async def profile_menu(notifications_enabled: bool = True) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        status_text = (
            "🔔 Уведомления выкл" if notifications_enabled else "🔔 Уведомления вкл"
        )
        builder.button(text=status_text, callback_data="notify_toggle")
        builder.button(text="📢 Перейти в канал", url="https://t.me/asic_plus")
        builder.button(text="💸 Хочу другую цену", callback_data="better_price")
        builder.button(text="🔙 Назад", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def devices_pagination(
        current_page: int, total_pages: int
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if current_page > 0:
            builder.button(
                text="⬅️ Назад", callback_data=f"devices_page:{current_page - 1}"
            )

        if current_page < total_pages - 1:
            builder.button(
                text="Вперёд ➡️", callback_data=f"devices_page:{current_page + 1}"
            )

        builder.button(text="🔙 Назад в меню", callback_data="calc_income")
        builder.adjust(2)
        return builder.as_markup()
