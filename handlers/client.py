from typing import Any, Dict

from aiogram import F, types
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database.models import Algorithm, Manufacturer
from keyboards.calculator_kb import CalculatorKB
from keyboards.client_kb import ClientKB
from signature import Settings
from utils.ai_service import ask_ishushka, create_chat
from utils.states import BetterPriceState, CalculatorState, FreeAiState, SellForm

user_chats: Dict[int, str] = {}


class ChannelFilter(Filter):
    def __init__(self, channel_id: int):
        self.channel_id = channel_id

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id == self.channel_id


class Client:
    def __init__(self, bot: Settings):
        self.bot = bot.bot
        self.dp = bot.dp
        self.settings = bot
        self.user_req = bot.user_req
        self.calculator_req = bot.calculator_req
        self.coin_req = bot.coin_req
        self.sell_req = bot.sell_req
        self.guide_req = bot.guide_req
        self.latest_price_link = None

    async def register_handlers(self):
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(Command("sell"))(self.sell_start_handler)
        self.dp.message(Command("by"))(self.by_handler)

        self.dp.channel_post(ChannelFilter(-1002725954632))(
            self.channel_message_handler
        )

        self.dp.callback_query(F.data == "back_main")(self.start_handler)
        self.dp.callback_query(F.data == "calc_income")(self.calc_income_handler)
        self.dp.callback_query(F.data == "price_list")(self.price_list_handler)
        self.dp.callback_query(F.data == "profile")(self.profile_handler)
        self.dp.callback_query(F.data == "calc_calc")(self.calc_calc_handler)
        self.dp.callback_query(F.data == "calc_chars")(self.calc_chars_handler)
        self.dp.callback_query(F.data == "calc_coins")(self.calc_coins_handler)
        self.dp.callback_query(F.data == "notify_toggle")(self.notify_toggle_handler)

        self.dp.callback_query(F.data == "better_price")(self.better_price_handler)
        self.dp.message(
            BetterPriceState.waiting_photo,
            F.content_type == ContentType.PHOTO,
        )(self.receive_better_price_photo)
        self.dp.message(
            BetterPriceState.waiting_comment,
            F.content_type == ContentType.TEXT,
        )(self.receive_better_price_comment)
        self.dp.callback_query(
            F.data.in_({"send_bp", "cancel_bp"}),
            BetterPriceState.waiting_confirm,
        )(self.confirm_better_price)

        self.dp.callback_query(F.data == "ai_consult")(self.ai_consult_start)
        self.dp.message(FreeAiState.chat)(self.ai_chat_handler)

        self.dp.callback_query(F.data.startswith("calc_method:"))(
            self.calc_method_handler
        )
        self.dp.callback_query(F.data.startswith("calc_manufacturer:"))(
            self.calc_manufacturer_handler
        )
        self.dp.callback_query(F.data.startswith("calc_model:"))(
            self.calc_model_handler
        )
        self.dp.callback_query(F.data == "calc_usd")(self.calc_usd_handler)
        self.dp.callback_query(F.data.startswith("calc_algorithm:"))(
            self.calc_algorithm_handler
        )
        self.dp.callback_query(F.data == "back_calc_method")(
            self.back_calc_method_handler
        )
        self.dp.callback_query(F.data == "back_calc_manufacturer")(
            self.back_calc_manufacturer_handler
        )
        self.dp.callback_query(F.data == "back_calc_model")(
            self.back_calc_model_handler
        )
        self.dp.callback_query(F.data == "back_calc_algorithm")(
            self.back_calc_algorithm_handler
        )
        self.dp.callback_query(F.data == "back_calc_hashrate")(
            self.back_calc_hashrate_handler
        )
        self.dp.callback_query(F.data == "calc_rub")(self.calc_rub_handler)

        self.dp.message(CalculatorState.input_electricity_price)(
            self.calc_electricity_handler
        )
        self.dp.message(CalculatorState.input_hashrate)(self.calc_hashrate_handler)
        self.dp.message(CalculatorState.input_power)(self.calc_power_handler)

        self.dp.message(SellForm.device)(self.sell_device_handler)
        self.dp.message(SellForm.price)(self.sell_price_handler)
        self.dp.message(SellForm.condition)(self.sell_condition_handler)
        self.dp.message(SellForm.description)(self.sell_description_handler)
        self.dp.message(SellForm.contact)(self.sell_contact_handler)

        self.dp.callback_query(F.data.startswith("devices_page:"))(
            self.devices_page_handler
        )

    async def channel_message_handler(self, message: types.Message):
        try:
            if message.text and "АКТУАЛЬНЫЙ ПРАЙС" in message.text.upper():
                channel_username = message.chat.username
                message_id = message.message_id

                if message.chat.username:
                    link = f"https://t.me/{channel_username}/{message_id}"
                else:
                    id_channel = f"{message.chat.id}"
                    link = f"https://t.me/c/{id_channel.split('-100')[1]}/{message_id}"
                await self.calculator_req.update_link(link)
                print(f"Обнаружен актуальный прайс: {link}")

        except Exception as e:
            print(f"Ошибка при обработке сообщения из канала: {e}")

    async def start_handler(
        self, message: types.Message | types.CallbackQuery, state: FSMContext
    ):
        await state.clear()
        if isinstance(message, types.CallbackQuery):
            user = message.from_user
            message_obj = message.message
            try:
                await message.answer()
            except TelegramBadRequest:
                pass
        else:
            user = message.from_user
            message_obj = message

        if not await self.user_req.user_exists(user.id):
            await self.user_req.add_user(user.id, user.username or user.first_name)

        text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Я AI-консультант по майнингу криптовалют. "
            "Помогу рассчитать доходность, подобрать оборудование и ответить на все вопросы."
        )
        photo = "https://i.yapx.ru/aaABM.png"
        kb = await ClientKB.main_menu()

        if isinstance(message, types.CallbackQuery):
            await message_obj.delete()
            await self.bot.send_photo(
                chat_id=user.id, photo=photo, caption=text, reply_markup=kb
            )
        else:
            await self.bot.send_photo(
                chat_id=user.id, photo=photo, caption=text, reply_markup=kb
            )

    async def calc_income_handler(self, call: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await call.message.delete()
        kb = await ClientKB.calc_menu()
        await self.bot.send_message(
            call.from_user.id, "💰 Выберите нужный раздел:", reply_markup=kb
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def price_list_handler(self, call: types.CallbackQuery):
        try:
            link = await self.calculator_req.get_link()
            if link:
                await call.message.answer(
                    f"📋 [Актуальный прайс-лист]({link})",
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            else:
                await call.message.answer("❌ Актуальный прайс-лист пока недоступен")

        except Exception as e:
            print(f"Ошибка при поиске прайса: {e}")
            await call.message.answer("❌ Ошибка при поиске прайса")

        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def profile_handler(self, call: types.CallbackQuery):
        await call.message.delete()
        notifications_status = await self.user_req.get_user_notifications_status(
            call.from_user.id
        )
        kb = await ClientKB.profile_menu(notifications_status)
        await self.bot.send_message(
            call.from_user.id, "👤 Ваш профиль:", reply_markup=kb
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_calc_handler(self, call: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await call.message.edit_text(
            "⚙️ Выберите способ расчета:",
            reply_markup=await CalculatorKB.choose_method(),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_chars_handler(
        self, call: types.CallbackQuery, state: FSMContext = None
    ):
        if state:
            await state.clear()

        devices = await self.calculator_req.get_all_asic_models()
        if not devices:
            await call.message.edit_text("❌ Нет данных об оборудовании")
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return

        await state.update_data(all_devices=devices, current_page=0)
        await self.show_devices_page(call, devices, 0)

    async def show_devices_page(
        self, call: types.CallbackQuery, devices: list, page: int
    ):
        items_per_page = 8
        total_pages = (len(devices) + items_per_page - 1) // items_per_page

        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(devices))
        current_devices = devices[start_idx:end_idx]

        message = f"📊 Характеристики оборудования (стр. {page + 1}/{total_pages}):\n\n"
        for device in current_devices:
            message += (
                f"🏷️ {device.manufacturer.value} {device.name}\n"
                f"   ⚙️ Алгоритм: {device.algorithm.value}\n"
                f"   ⚡ Хешрейт: {device.hash_rate} {'TH/s' if device.hash_rate > 1 else 'GH/s'}\n"
                f"   🔌 Потребление: {device.power_consumption}W\n"
                f"   💰 Цена: ${device.price_usd}\n"
                f"   🪙 Добывает: {device.get_coin if device.get_coin else 'Не указано'}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )

        kb = await ClientKB.devices_pagination(page, total_pages)
        await call.message.edit_text(message, reply_markup=kb)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def devices_page_handler(self, call: types.CallbackQuery, state: FSMContext):
        page = int(call.data.split(":")[1])
        data = await state.get_data()
        devices = data["all_devices"]
        await state.update_data(current_page=page)
        await self.show_devices_page(call, devices, page)

    async def calc_coins_handler(self, call: types.CallbackQuery):
        coins = await self.coin_req.get_all_coins()
        if not coins:
            await call.message.edit_text("❌ Нет данных о ценах монет")
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return

        message = "💎 Текущие цены монет:\n\n"
        for coin in coins:
            change_icon = "📈" if coin.price_change_24h >= 0 else "📉"
            change_text = f"{coin.price_change_24h:+.1f}%"

            message += (
                f"🔸 {coin.symbol} ({coin.name})\n"
                f"   💵 ${coin.current_price_usd:,.2f} | ₽{coin.current_price_rub:,.0f}\n"
                f"   {change_icon} {change_text}\n"
                f"   📅 Обновлено: {coin.last_updated.strftime('%d.%m.%Y %H:%M')}\n\n"
            )

        message += "Цены обновляются ежедневно в 10:00 по Москве 🕙"
        await call.message.edit_text(message, reply_markup=await ClientKB.back_calc())
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def notify_toggle_handler(self, call: types.CallbackQuery):
        new_status = await self.user_req.toggle_notifications(call.from_user.id)
        status_text = "включены" if new_status else "выключены"
        kb = await ClientKB.profile_menu(new_status)
        await call.message.edit_text(f"🔔 Уведомления {status_text}", reply_markup=kb)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def better_price_handler(self, call: types.CallbackQuery, state: FSMContext):
        await call.message.delete()
        await self.bot.send_message(
            call.from_user.id,
            "📸 Пришлите скриншот, где видно предложение конкурента:",
        )
        await state.set_state(BetterPriceState.waiting_photo)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def receive_better_price_photo(
        self, message: types.Message, state: FSMContext
    ):
        photo_file_id = message.photo[-1].file_id
        await state.update_data(photo=photo_file_id)
        await message.answer("💬 Добавьте комментарий (что именно хотите изменить):")
        await state.set_state(BetterPriceState.waiting_comment)

    async def receive_better_price_comment(
        self, message: types.Message, state: FSMContext
    ):
        await state.update_data(comment=message.text)
        data = await state.get_data()

        await message.answer_photo(
            photo=data["photo"],
            caption=f"<b>Предпросмотр:</b>\n\n{data['comment']}",
            parse_mode="HTML",
            reply_markup=await ClientKB.confirm_a(),
        )
        await state.set_state(BetterPriceState.waiting_confirm)

    async def confirm_better_price(self, call: types.CallbackQuery, state: FSMContext):
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

        if call.data == "cancel_bp":
            await call.message.edit_caption(caption="Отменено.")
            await state.clear()
            return

        data = await state.get_data()
        user = call.from_user
        try:
            await self.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=data["photo"],
                caption=(
                    f"<b>Заявка «Лучшая цена»</b>\n"
                    f"От: {user.username}\n"
                    f"ID: <code>{user.id}</code>\n\n"
                    f"{data['comment']}"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            print(e)
            await call.message.edit_caption(
                caption="❌ Не удалось отправить заявку. Попробуйте позже."
            )
            await state.clear()
            return

        await call.message.edit_caption(
            caption="✅ Спасибо! Менеджер скоро свяжется с вами."
        )
        await state.clear()

    async def by_handler(self, message: types.Message):
        guide = await self.guide_req.get_guide()
        if guide:
            message_text = f"📖 {guide.title}\n\n{guide.content}"
            await message.answer(message_text)
        else:
            await message.answer("❌ Руководство по б/у устройствам пока не доступно")

    async def sell_start_handler(self, message: types.Message, state: FSMContext):
        devices = await self.calculator_req.get_all_asic_models()
        if not devices:
            await message.answer("❌ Нет данных об оборудовании")
            return
        message_text = "🎯 Выберите тип оборудования для продажи:\n\n"
        for device in devices:
            message_text += (
                f"🔹 {device.id}. {device.manufacturer.value} {device.name}\n"
            )
        message_text += "\nВведите номер оборудования:"
        await message.answer(message_text)
        await state.set_state(SellForm.device)

    async def sell_device_handler(self, message: types.Message, state: FSMContext):
        try:
            device_id = int(message.text)
            device = await self.calculator_req.get_asic_model_by_id(device_id)
            if not device:
                await message.answer(
                    "❌ Неверный номер оборудования. Попробуйте снова:"
                )
                return
            await state.update_data(device_id=device_id)
            await message.answer(
                f"💵 Введите цену продажи для {device.manufacturer.value} {device.name} (USD):"
            )
            await state.set_state(SellForm.price)
        except ValueError:
            await message.answer("❌ Введите корректный номер оборудования:")

    async def sell_price_handler(self, message: types.Message, state: FSMContext):
        try:
            price = float(message.text.replace(",", "."))
            await state.update_data(price=price)
            await message.answer(
                "📝 Опишите состояние оборудования (новое/б/у/отличное/хорошее):"
            )
            await state.set_state(SellForm.condition)
        except ValueError:
            await message.answer("❌ Введите корректную цену:")

    async def sell_condition_handler(self, message: types.Message, state: FSMContext):
        await state.update_data(condition=message.text)
        await message.answer(
            "📋 Опишите подробнее ваше оборудование (год покупки, наработка часов и т.д.):"
        )
        await state.set_state(SellForm.description)

    async def sell_description_handler(self, message: types.Message, state: FSMContext):
        await state.update_data(description=message.text)
        await message.answer(
            "📞 Введите контактную информацию для связи (телеграм @username или телефон):"
        )
        await state.set_state(SellForm.contact)

    async def sell_contact_handler(self, message: types.Message, state: FSMContext):
        await state.update_data(contact=message.text)
        data = await state.get_data()
        device = await self.calculator_req.get_asic_model_by_id(data["device_id"])
        user = await self.user_req.get_user_by_uid(message.from_user.id)
        request_id = await self.sell_req.create_sell_request(
            user_id=user.id,
            device_id=data["device_id"],
            price=data["price"],
            condition=data["condition"],
            description=data["description"],
            contact_info=data["contact"],
        )
        response_message = (
            "✅ Заявка на продажу создана!\n\n"
            f"🏷️ Оборудование: {device.manufacturer.value} {device.name}\n"
            f"💵 Цена: ${data['price']}\n"
            f"📝 Состояние: {data['condition']}\n"
            f"📞 Контакты: {data['contact']}\n\n"
            "Менеджер свяжется с вами в ближайшее время."
        )
        await message.answer(response_message, reply_markup=await ClientKB.main_menu())
        await state.clear()

    async def calc_method_handler(self, call: types.CallbackQuery, state: FSMContext):
        method = call.data.split(":")[1]
        await state.update_data(calc_method=method)
        if method == "asic":
            await call.message.edit_text(
                "🏭 Выберите производителя:",
                reply_markup=await CalculatorKB.choose_manufacturer(),
            )
        else:
            await call.message.edit_text(
                "⚙️ Выберите алгоритм для расчета:",
                reply_markup=await CalculatorKB.choose_algorithm(),
            )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_manufacturer_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        manufacturer_name = call.data.split(":")[1]
        manufacturer = Manufacturer(manufacturer_name)
        await state.update_data(manufacturer=manufacturer)
        models = await self.calculator_req.get_asic_models_by_manufacturer(manufacturer)
        if not models:
            await call.message.edit_text("❌ Нет моделей для этого производителя")
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return
        await call.message.edit_text(
            "📱 Выберите модель ASIC-майнера для расчёта:",
            reply_markup=await CalculatorKB.choose_asic_models(models),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_model_handler(self, call: types.CallbackQuery, state: FSMContext):
        model_id = int(call.data.split(":")[1])
        await state.update_data(model_id=model_id)
        await call.message.edit_text(
            "💡 Введите цену на электроэнергию (кВт/ч) в рублях\n\nПример: 7.3",
            reply_markup=await CalculatorKB.electricity_input(),
        )
        await state.set_state(CalculatorState.input_electricity_price)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_algorithm_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        algorithm_value = call.data.split(":")[1]
        algorithm = None
        for algo in Algorithm:
            if algo.value == algorithm_value:
                algorithm = algo
                break
        if algorithm is None:
            await call.message.edit_text("❌ Алгоритм не найден")
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return
        await state.update_data(algorithm=algorithm)
        await call.message.edit_text(
            "💡 Введите цену на электроэнергию (кВт/ч) в рублях\n\nПример: 7.3",
            reply_markup=await CalculatorKB.electricity_input(),
        )
        await state.set_state(CalculatorState.input_electricity_price)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_usd_handler(self, call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        result = data["calculation_result"]
        coin_symbol = data["coin_symbol"]
        from utils.calculator import MiningCalculator

        text = (
            f"🔧 **Оборудование:** {data.get('model_name', '')}\n"
            if data.get("model_name")
            else ""
        )
        text += (
            f"⚙️ **Алгоритм:** {data.get('algorithm_name', '')}\n"
            if data.get("algorithm_name")
            else ""
        )
        text += f"💰 **Криптовалюта:** {data.get('coin_name', '')} ({coin_symbol})\n"
        text += f"📈 **Курс {coin_symbol}:** ${data['coin_price']:.4f}\n"
        text += f"💵 **Курс доллара:** {80.0} руб.\n\n"
        text += MiningCalculator.format_result(result, coin_symbol)

        await call.message.edit_text(
            text, reply_markup=await CalculatorKB.result_menu()
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def calc_electricity_handler(self, message: types.Message, state: FSMContext):
        try:
            electricity_price = float(message.text.replace(",", "."))
            await state.update_data(electricity_price=electricity_price)
            data = await state.get_data()
            if data.get("calc_method") == "asic":
                await self.calculate_profitability(message, state)
            else:
                await message.answer(
                    "⚡ Введите количество хешрейта (GH/s)\n\nПример: 110",
                    reply_markup=await CalculatorKB.hashrate_input(),
                )
                await state.set_state(CalculatorState.input_hashrate)
        except ValueError:
            await message.answer("❌ Введите корректное число:")

    async def calc_hashrate_handler(self, message: types.Message, state: FSMContext):
        try:
            hashrate = float(message.text.replace(",", "."))
            await state.update_data(hashrate=hashrate)
            await message.answer(
                "🔌 Введите суммарную мощность (Вт)\n\nПример: 3250",
                reply_markup=await CalculatorKB.power_input(),
            )
            await state.set_state(CalculatorState.input_power)
        except ValueError:
            await message.answer("❌ Введите корректное число:")

    async def calc_power_handler(self, message: types.Message, state: FSMContext):
        try:
            power = float(message.text.replace(",", "."))
            await state.update_data(power=power)
            await self.calculate_profitability(message, state)
        except ValueError:
            await message.answer("❌ Введите корректное число:")

    async def calculate_profitability(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        electricity_price_rub = data["electricity_price"]
        electricity_price_usd = electricity_price_rub / 80.0

        if data.get("calc_method") == "asic":
            model = await self.calculator_req.get_asic_model_by_id(data["model_id"])
            algorithm_data = await self.calculator_req.get_algorithm_data(
                model.algorithm
            )
            if not algorithm_data:
                await message.answer(
                    "❌ Для выбранного алгоритма нет данных. Обратитесь к администратору."
                )
                return
            coin = await self.calculator_req.get_coin_by_symbol(
                algorithm_data.default_coin
            )
            if not coin:
                await message.answer(
                    "❌ Цена для монеты не установлена. Обратитесь к администратору."
                )
                return
            hash_rate = model.hash_rate
            power_consumption = model.power_consumption
            algorithm_dict = {
                "network_hashrate": algorithm_data.network_hashrate,
                "block_reward": algorithm_data.block_reward,
            }
            text = f"🔧 **Оборудование:** {model.manufacturer.value} {model.name}\n"
            text += (
                f"⚡ **Хэшрейт:** {hash_rate} {'TH/s' if hash_rate > 1 else 'GH/s'}\n\n"
            )
        else:
            algorithm = data["algorithm"]
            algorithm_data = await self.calculator_req.get_algorithm_data(algorithm)
            if not algorithm_data:
                await message.answer(
                    "❌ Для выбранного алгоритма нет данных. Обратитесь к администратору."
                )
                return
            print(algorithm_data.default_coin)
            coin = await self.calculator_req.get_coin_by_symbol(
                algorithm_data.default_coin
            )
            print(coin)
            if not coin:
                await message.answer(
                    "❌ Цена для монета не установлена. Обратитесь к администратору."
                )
                return
            hash_rate = data["hashrate"]
            power_consumption = data["power"]
            algorithm_dict = {
                "network_hashrate": algorithm_data.network_hashrate,
                "block_reward": algorithm_data.block_reward,
            }
            text = f"⚙️ **Алгоритм:** {algorithm.value}\n"
            text += f"⚡ **Хэшрейт:** {hash_rate} GH/s\n"
            text += f"🔌 **Мощность:** {power_consumption} W\n\n"

        from utils.calculator import MiningCalculator

        result = MiningCalculator.calculate_profitability(
            hash_rate=hash_rate,
            power_consumption=power_consumption,
            electricity_price=electricity_price_usd,
            coin_price=coin.current_price_usd,
            algorithm_data=algorithm_dict,
        )
        text += f"💰 **Криптовалюта:** {coin.name} ({coin.symbol})\n"
        text += f"📈 **Курс {coin.symbol}:** ${coin.current_price_usd:.4f}\n"
        text += f"💵 **Курс доллара:** {80.0} руб.\n\n"
        text += MiningCalculator.format_result(result, coin.symbol)
        await state.update_data(
            calculation_result=result,
            coin_symbol=coin.symbol,
            coin_name=coin.name,
            coin_price=coin.current_price_usd,
            model_name=(
                f"{model.manufacturer.value} {model.name}"
                if data.get("calc_method") == "asic"
                else ""
            ),
            algorithm_name=(
                algorithm.value if data.get("calc_method") == "hashrate" else ""
            ),
        )
        await state.set_state(CalculatorState.show_result)
        await message.answer(text, reply_markup=await CalculatorKB.result_menu())

    async def calc_rub_handler(self, call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        result = data["calculation_result"]
        coin_symbol = data["coin_symbol"]
        from utils.calculator import MiningCalculator

        text = MiningCalculator.format_result_rub(result, coin_symbol)
        await call.message.edit_text(
            text, reply_markup=await CalculatorKB.result_menu_rub()
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def back_calc_method_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        await call.message.edit_text(
            "⚙️ Выберите способ расчета:",
            reply_markup=await CalculatorKB.choose_method(),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def back_calc_manufacturer_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        await call.message.edit_text(
            "🏭 Выберите производителя:",
            reply_markup=await CalculatorKB.choose_manufacturer(),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def back_calc_model_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        data = await state.get_data()

        if data.get("calc_method") != "asic":
            await call.message.edit_text(
                "⚙️ Выберите алгоритм для расчета:",
                reply_markup=await CalculatorKB.choose_algorithm(),
            )
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return

        if "manufacturer" not in data:
            await call.message.edit_text(
                "⚙️ Выберите способ расчета:",
                reply_markup=await CalculatorKB.choose_method(),
            )
            try:
                await call.answer()
            except TelegramBadRequest:
                pass
            return

        manufacturer = data["manufacturer"]
        models = await self.calculator_req.get_asic_models_by_manufacturer(manufacturer)
        await call.message.edit_text(
            "📱 Выберите модель ASIC-майнера для расчёта:",
            reply_markup=await CalculatorKB.choose_asic_models(models),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def back_calc_algorithm_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        await call.message.edit_text(
            "⚙️ Выберите алгоритм для расчета:",
            reply_markup=await CalculatorKB.choose_algorithm(),
        )
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def back_calc_hashrate_handler(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        await call.message.edit_text(
            "⚡ Введите количество хешрейта (GH/s)\n\nПример: 110",
            reply_markup=await CalculatorKB.hashrate_input(),
        )
        await state.set_state(CalculatorState.input_hashrate)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def ai_consult_start(self, call: types.CallbackQuery, state: FSMContext):
        uid = call.from_user.id
        if uid not in user_chats:
            user_chats[uid] = await create_chat()
        await call.message.delete()
        await self.bot.send_message(
            uid,
            text=(
                "👋 **Добро пожаловать в AI-консультант ASIC+!**\n\n"
                "Задайте любой вопрос по майнинку, оборудованию, доходности.\n\n"
                "Примеры:\n"
                "• «Какой ASIC выгодно купить за 3000$?»\n"
                "• «Какая сейчас прибыль от S19 XP?»\n"
                "• «Покажи прайс»\n\n"
                "⏳ Ответ обычно приходит за 3–5 секунд."
            ),
            reply_markup=await ClientKB.back_ai(),
        )
        await state.set_state(FreeAiState.chat)
        try:
            await call.answer()
        except TelegramBadRequest:
            pass

    async def ai_chat_handler(self, message: types.Message, state: FSMContext):
        uid = message.from_user.id
        conv_id = user_chats[uid]

        asics = await self.calculator_req.get_all_asic_models()
        coins = await self.coin_req.get_all_coins()

        context = {
            "asic_models": [
                {
                    "name": a.name,
                    "manufacturer": a.manufacturer.value,
                    "algorithm": a.algorithm.value,
                    "hash_rate": a.hash_rate,
                    "power": a.power_consumption,
                    "price": a.price_usd,
                    "full_info": f"{a.manufacturer.value} {a.name} ({a.algorithm.value}, {a.hash_rate} {'TH/s' if a.hash_rate > 1 else 'GH/s'}, {a.power_consumption}W, ${a.price_usd})",
                }
                for a in asics
            ],
            "coins": [
                {
                    "symbol": c.symbol,
                    "price": c.current_price_usd,
                    "name": c.name,
                    "full_info": f"{c.symbol} ({c.name}): ${c.current_price_usd:.4f}",
                }
                for c in coins
            ],
        }

        wait_msg = await message.answer(
            "⏳ **AI анализирует данные…**", parse_mode="Markdown"
        )

        answer = await ask_ishushka(conv_id, message.text, context)
        await self.bot.delete_message(
            chat_id=message.chat.id, message_id=wait_msg.message_id
        )

        safe_answer = escape_html(answer)
        await message.answer(safe_answer, reply_markup=await ClientKB.back_ai())


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
