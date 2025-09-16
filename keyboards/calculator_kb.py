from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Algorithm, Manufacturer


class CalculatorKB:
    @staticmethod
    async def choose_method() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="ASIC-майнер", callback_data="calc_method:asic")
        builder.button(text="По хешрейту", callback_data="calc_method:hashrate")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def choose_manufacturer() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for manufacturer in Manufacturer:
            builder.button(
                text=manufacturer.value,
                callback_data=f"calc_manufacturer:{manufacturer.value}",
            )
        builder.button(text="🔙 Назад", callback_data="back_calc_method")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def result_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Рассчитать в рублях", callback_data="calc_rub")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def result_menu_rub() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="💵 Рассчитать в долларах", callback_data="calc_usd")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def choose_model_lines(
        model_lines: list, page: int = 0, lines_per_page: int = 8
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        start_idx = page * lines_per_page
        end_idx = start_idx + lines_per_page
        paginated_lines = model_lines[start_idx:end_idx]

        for line in paginated_lines:
            builder.button(text=line.name, callback_data=f"calc_line:{line.id}")

        if page > 0:
            builder.button(text="⬅️ Назад", callback_data=f"calc_lines_page:{page-1}")
        if end_idx < len(model_lines):
            builder.button(text="Вперед ➡️", callback_data=f"calc_lines_page:{page+1}")

        builder.button(text="🔙 Назад", callback_data="back_calc_manufacturer")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def choose_asic_models_by_line(
        models: list, model_line_name: str, page: int = 0, models_per_page: int = 8
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        start_idx = page * models_per_page
        end_idx = start_idx + models_per_page
        paginated_models = models[start_idx:end_idx]

        for model in paginated_models:
            builder.button(text=model.name, callback_data=f"calc_model:{model.id}")

        if page > 0:
            builder.button(text="⬅️ Назад", callback_data=f"calc_models_page:{page-1}")
        if end_idx < len(models):
            builder.button(text="Вперед ➡️", callback_data=f"calc_models_page:{page+1}")

        builder.button(text="🔙 Назад", callback_data=f"back_calc_line")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def choose_algorithm() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for algorithm in Algorithm:
            builder.button(
                text=algorithm.value, callback_data=f"calc_algorithm:{algorithm.value}"
            )
        builder.button(text="🔙 Назад", callback_data="back_calc_method")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def back_to_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def electricity_input() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="back_calc_model")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def hashrate_input() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="back_calc_algorithm")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def power_input() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="back_calc_hashrate")
        builder.button(text="🔙 Главное меню", callback_data="back_main")
        builder.adjust(1)
        return builder.as_markup()
