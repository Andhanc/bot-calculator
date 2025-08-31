import os

from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.models import Algorithm, AlgorithmData, AsicModel, Coin, Manufacturer
from database.request import CalculatorReq, CoinReq
from keyboards.admin_kb import AdminKB
from signature import Settings

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))


class AdminStates(StatesGroup):
    broadcast_text = State()
    broadcast_photo = State()
    reply_to_user = State()
    add_asic_name = State()
    add_asic_manufacturer = State()
    add_asic_algorithm = State()
    add_asic_hashrate = State()
    add_asic_power = State()
    add_asic_price = State()
    add_asic_get_coin = State()
    edit_coin_price = State()
    algo_default_coin = State()
    algo_difficulty = State()
    algo_network = State()
    algo_reward = State()


class Admin:
    def __init__(self, bot: Settings):
        self.bot = bot.bot
        self.dp = bot.dp
        self.settings = bot
        self.calc_req = CalculatorReq(bot.db_manager.async_session)
        self.coin_req = CoinReq(bot.db_manager.async_session)

    async def register_handler(self):
        self.dp.message(Command("admin"))(self.admin_menu)
        self.dp.callback_query(F.data == "admin_menu")(self.admin_menu)

        self.dp.callback_query(F.data == "broadcast_start")(self.broadcast_start)
        self.dp.message(AdminStates.broadcast_text)(self.broadcast_text)
        self.dp.message(AdminStates.broadcast_photo, F.content_type == "photo")(
            self.broadcast_photo
        )
        self.dp.message(AdminStates.broadcast_photo, F.content_type == "text")(
            self.broadcast_no_photo
        )

        self.dp.callback_query(F.data == "admin_menu", AdminStates.broadcast_photo)(
            self.admin_menu_from_broadcast
        )
        self.dp.callback_query(F.data == "admin_menu", AdminStates.broadcast_text)(
            self.admin_menu_from_broadcast
        )

        self.dp.callback_query(F.data == "manage_asic")(self.manage_asic)
        self.dp.callback_query(F.data == "add_asic")(self.add_asic_start)
        self.dp.callback_query(F.data.startswith("manufacturer:"))(
            self.handle_manufacturer_selection
        )
        self.dp.callback_query(F.data.startswith("algorithm:"))(
            self.handle_algorithm_selection
        )
        self.dp.message(AdminStates.add_asic_name)(self.add_asic_name)
        self.dp.message(AdminStates.add_asic_hashrate)(self.add_asic_hashrate)
        self.dp.message(AdminStates.add_asic_power)(self.add_asic_power)
        self.dp.message(AdminStates.add_asic_price)(self.add_asic_price)
        self.dp.message(AdminStates.add_asic_get_coin)(self.add_asic_get_coin)
        self.dp.callback_query(F.data.startswith("delete_asic:"))(self.delete_asic)

        self.dp.callback_query(F.data == "manage_coins")(self.manage_coins)
        self.dp.callback_query(F.data.startswith("edit_coin:"))(self.edit_coin_start)
        self.dp.message(AdminStates.edit_coin_price)(self.edit_coin_price)

        self.dp.callback_query(F.data == "manage_algorithms")(self.manage_algorithms)
        self.dp.callback_query(F.data.startswith("edit_algo:"))(self.edit_algo_start)
        self.dp.message(AdminStates.algo_default_coin)(self.edit_algo_coin)
        self.dp.message(AdminStates.algo_difficulty)(self.edit_algo_difficulty)
        self.dp.message(AdminStates.algo_network)(self.edit_algo_network)
        self.dp.message(AdminStates.algo_reward)(self.edit_algo_reward)

        self.dp.message(F.content_type == "photo", lambda m: m.chat.type == "private")(
            self.handle_user_photo
        )

    def is_admin(self, user_id: int) -> bool:
        return user_id in ADMIN_IDS

    async def admin_menu(self, event: types.Message | types.CallbackQuery):
        if isinstance(event, types.CallbackQuery):
            await event.answer()
            user_id = event.from_user.id
        else:
            user_id = event.from_user.id
        if not self.is_admin(user_id):
            return await event.answer("❌ Нет доступа")
        kb = await AdminKB.admin_menu()
        text = "🔐 Админ-панель"
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=kb)
        else:
            await event.answer(text, reply_markup=kb)

    async def broadcast_start(self, call: types.CallbackQuery, state: FSMContext):
        await call.message.edit_text("📢 Введите текст рассылки:")
        await state.set_state(AdminStates.broadcast_text)

    async def broadcast_text(self, message: types.Message, state: FSMContext):
        await state.update_data(text=message.text)
        await message.answer(
            "📷 Прикрепите фото или отправьте 'нет' без кавычек:",
            reply_markup=await AdminKB.broadcast_back(),
        )
        await state.set_state(AdminStates.broadcast_photo)

    async def broadcast_photo(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        text = data["text"]
        photo = message.photo[-1].file_id
        users = await self.settings.user_req.get_all_users()

        success_count = 0
        fail_count = 0

        for u in users:
            try:
                await self.bot.send_photo(u.uid, photo, caption=text)
                success_count += 1
            except Exception:
                fail_count += 1

        await message.answer(
            f"✅ Рассылка завершена\n"
            f"✅ Успешно: {success_count}\n"
            f"❌ Не доставлено: {fail_count}",
            reply_markup=await AdminKB.admin_menu(),
        )
        await state.clear()

    async def broadcast_no_photo(self, message: types.Message, state: FSMContext):
        if message.text.lower() == "нет":
            data = await state.get_data()
            text = data["text"]
            users = await self.settings.user_req.get_all_users()

            success_count = 0
            fail_count = 0

            for u in users:
                try:
                    await self.bot.send_message(u.uid, text)
                    success_count += 1
                except Exception:
                    fail_count += 1

            await message.answer(
                f"✅ Рассылка завершена\n"
                f"✅ Успешно: {success_count}\n"
                f"❌ Не доставлено: {fail_count}",
                reply_markup=await AdminKB.admin_menu(),
            )
            await state.clear()
        else:
            await message.answer("❌ Отправьте фото или напишите 'нет'")

    async def admin_menu_from_broadcast(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        await state.clear()
        await self.admin_menu(call)

    async def manage_asic(self, call: types.CallbackQuery):
        models = await self.calc_req.get_all_asic_models()
        kb = await AdminKB.list_asic(models)
        await call.message.edit_text("⚙️ Управление ASIC:", reply_markup=kb)

    async def add_asic_start(self, call: types.CallbackQuery, state: FSMContext):
        await call.message.edit_text("🏷️ Введите название ASIC:")
        await state.set_state(AdminStates.add_asic_name)

    async def add_asic_name(self, message: types.Message, state: FSMContext):
        await state.update_data(name=message.text)
        await message.answer(
            "🏭 Выберите производителя:",
            reply_markup=await AdminKB.choose_manufacturer(),
        )

    async def handle_manufacturer_selection(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        manufacturer = call.data.split(":")[1]
        await state.update_data(manufacturer=manufacturer)
        await call.message.edit_text(
            "⚙️ Выберите алгоритм:", reply_markup=await AdminKB.choose_algorithm()
        )

    async def handle_algorithm_selection(
        self, call: types.CallbackQuery, state: FSMContext
    ):
        algorithm = call.data.split(":")[1]
        await state.update_data(algorithm=algorithm)
        await call.message.edit_text("⚡ Введите хэшрейт (TH/s или GH/s):")
        await state.set_state(AdminStates.add_asic_hashrate)

    async def add_asic_hashrate(self, message: types.Message, state: FSMContext):
        try:
            rate = float(message.text.replace(",", "."))
            await state.update_data(hash_rate=rate)
            await message.answer("🔌 Введите потребление (Вт):")
            await state.set_state(AdminStates.add_asic_power)
        except ValueError:
            await message.answer("❌ Введите число")

    async def add_asic_power(self, message: types.Message, state: FSMContext):
        try:
            power = float(message.text.replace(",", "."))
            await state.update_data(power=power)
            await message.answer("💰 Введите цену в USD:")
            await state.set_state(AdminStates.add_asic_price)
        except ValueError:
            await message.answer("❌ Введите число")

    async def add_asic_price(self, message: types.Message, state: FSMContext):
        try:
            price = float(message.text.replace(",", "."))
            await state.update_data(price_usd=price)
            await message.answer(
                "💰 Введите добываемые монеты (через пробел, например: BTC ETH):"
            )
            await state.set_state(AdminStates.add_asic_get_coin)
        except ValueError:
            await message.answer("❌ Введите число")

    async def add_asic_get_coin(self, message: types.Message, state: FSMContext):
        try:
            get_coin = message.text.upper()
            data = await state.get_data()
            await self.calc_req.add_asic_model(
                name=data["name"],
                manufacturer=Manufacturer[data["manufacturer"]],
                algorithm=Algorithm[data["algorithm"]],
                hash_rate=data["hash_rate"],
                power_consumption=data["power"],
                price_usd=data["price_usd"],
                get_coin=get_coin,
            )
            await message.answer("✅ ASIC добавлен с информацией о добываемых монетах")
            await state.clear()
            await self.admin_menu(message)
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    async def delete_asic(self, call: types.CallbackQuery):
        model_id = int(call.data.split(":")[1])
        await self.calc_req.delete_asic_model(model_id)
        await call.answer("✅ ASIC удалён")
        await self.manage_asic(call)

    async def manage_coins(self, call: types.CallbackQuery):
        coins = await self.coin_req.get_all_coins()
        kb = await AdminKB.list_coins(coins)
        await call.message.edit_text("💰 Управление ценами монет:", reply_markup=kb)

    async def edit_coin_start(self, call: types.CallbackQuery, state: FSMContext):
        symbol = call.data.split(":")[1]
        await state.update_data(symbol=symbol)
        await call.message.edit_text(f"Введите новую цену для {symbol}:")
        await state.set_state(AdminStates.edit_coin_price)

    async def edit_coin_price(self, message: types.Message, state: FSMContext):
        try:
            price = float(message.text.replace(",", "."))
            data = await state.get_data()
            await self.coin_req.update_coin_price(data["symbol"], price)
            await message.answer("✅ Цена обновлена")
            await state.clear()
            await self.admin_menu(message)
        except ValueError:
            await message.answer("❌ Введите число")

    async def manage_algorithms(self, call: types.CallbackQuery):
        algos = await self.calc_req.get_algorithm_data_all()
        kb = await AdminKB.list_algorithms(algos)
        await call.message.edit_text("⚙️ Управление алгоритмами:", reply_markup=kb)

    async def edit_algo_start(self, call: types.CallbackQuery, state: FSMContext):
        algo_name = call.data.split(":")[1]
        await state.update_data(algorithm=Algorithm[algo_name])
        await call.message.edit_text("Введите монету по умолчанию:")
        await state.set_state(AdminStates.algo_default_coin)

    async def edit_algo_coin(self, message: types.Message, state: FSMContext):
        await state.update_data(default_coin=message.text.upper())
        await message.answer("Введите сложность:")
        await state.set_state(AdminStates.algo_difficulty)

    async def edit_algo_difficulty(self, message: types.Message, state: FSMContext):
        try:
            val = float(message.text)
            await state.update_data(difficulty=val)
            await message.answer("Введите сетевой хэшрейт:")
            await state.set_state(AdminStates.algo_network)
        except ValueError:
            await message.answer("❌ Введите число")

    async def edit_algo_network(self, message: types.Message, state: FSMContext):
        try:
            val = float(message.text)
            await state.update_data(network_hashrate=val)
            await message.answer("Введите награду за блок:")
            await state.set_state(AdminStates.algo_reward)
        except ValueError:
            await message.answer("❌ Введите число")

    async def edit_algo_reward(self, message: types.Message, state: FSMContext):
        try:
            val = float(message.text)
            data = await state.get_data()
            await self.calc_req.update_algorithm_data(
                algorithm=data["algorithm"],
                default_coin=data["default_coin"],
                difficulty=data["difficulty"],
                network_hashrate=data["network_hashrate"],
                block_reward=val,
            )
            await message.answer("✅ Данные алгоритма обновлены")
            await state.clear()
            await self.admin_menu(message)
        except ValueError:
            await message.answer("❌ Введите число")

    async def handle_user_photo(self, message: types.Message):
        current_state = await self.settings.dp.current_state().get_state()
        if current_state == AdminStates.broadcast_photo.state:
            return

        if self.is_admin(message.from_user.id):
            return

        for admin_id in ADMIN_IDS.split(","):
            try:
                await self.bot.forward_message(
                    admin_id, message.chat.id, message.message_id
                )
                await self.bot.send_message(
                    admin_id,
                    f"📸 От @{message.from_user.username or message.from_user.id}",
                    reply_markup=await AdminKB.reply_to_user(message.from_user.id),
                )
            except Exception:
                pass
