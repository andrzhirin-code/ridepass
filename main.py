import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Импорты ваших модулей
from database import init_db, add_user, add_order, get_order, update_order_status, get_pending_orders, get_user, update_user_balance
from image_filler import generate_pdf

# ---------- КОНФИГУРАЦИЯ ----------
API_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"
ADMIN_ID = 5171781123  # Ваш ID, убедитесь, что он верный

if not API_TOKEN:
    raise ValueError("No BOT_TOKEN found")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)

# ---------- КЛАВИАТУРЫ ----------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Получить документы")],
        [KeyboardButton(text="Заработай с нами/реферальная система")],
        [KeyboardButton(text="Связь с поддержкой")]
    ],
    resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]],
    resize_keyboard=True
)

# ---------- FSM ----------
class Form(StatesGroup):
    vehicle_type = State()
    custom_type = State()
    brand = State()
    model = State()
    year = State()
    power = State()
    custom_power = State()
    serial = State()
    full_name = State()
    passport = State()
    address = State()
    phone = State()
    speed = State()

# ---------- ВЕБ-СЕРВЕР ДЛЯ RENDER ----------
async def health_check(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

# ---------- СТАРТ ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # ... (весь код start без изменений, он у вас был рабочий) ...
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = int(args[1].split("_")[1])
    
    user_id = message.from_user.id
    bot_username = (await bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    add_user(user_id, referral_link)
    
    if referrer_id:
        update_user_balance(referrer_id, 500)
        await bot.send_message(referrer_id, "🎉 Вам начислено 500₽ за приглашённого друга!")
    
    await message.answer(
        "🌟 Добро пожаловать в RidePass 🌟\n\nОформление документов на электротранспорт — быстро, удобно и полностью онлайн.\n\n📋 Как получить документы:\n1️⃣ Нажмите «Получить документы»\n2️⃣ Выберите тип транспортного средства\n3️⃣ Укажите данные\n4️⃣ Оплатите фиксированную стоимость по реквизитам\n5️⃣ Нажмите «Я оплатил»\n6️⃣ Дождитесь подтверждения менеджера\n7️⃣ Получите готовый PDF-документ прямо в боте",
        reply_markup=main_menu
    )

# ---------- НАЗАД ----------
@dp.message(F.text == "Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu)

# ---------- ПОЛУЧИТЬ ДОКУМЕНТЫ (ВЕСЬ ВАШ РАБОЧИЙ КОД ОСТАЁТСЯ БЕЗ ИЗМЕНЕНИЙ) ----------
# ... (здесь должен быть весь ваш код FSM от @dp.message(F.text == "Получить документы") до @dp.message(F.text == "Я оплатил") ...
# Чтобы сэкономить место, я его пропускаю, но ВЫ ДОЛЖНЫ ВСТАВИТЬ ЕГО СЮДА ИЗ ВАШЕГО ТЕКУЩЕГО ФАЙЛА.
# Я пометил место звёздочками (******), куда нужно вставить ваш старый код, который мы не меняем.

# *****************************************************************************
# >>> СЮДА ВСТАВЬТЕ ВЕСЬ КОД FSM ИЗ ВАШЕГО СТАРОГО main.py (ОТ @dp.message(F.text == "Получить документы") ДО @dp.message(F.text == "Я оплатил") ВКЛЮЧИТЕЛЬНО) <<<
# *****************************************************************************


# ---------- НОВЫЙ ОБРАБОТЧИК ДЛЯ КНОПОК "Я ОПЛАТИЛ" (Он должен быть после вашего старого кода) ----------
@dp.message(F.text == "Я оплатил")
async def i_paid(message: types.Message):
    await message.answer(
        "🙏 Спасибо! Мы отправили администраторам уведомление о платеже.\n\n⏳ Дождитесь подтверждения.",
        reply_markup=main_menu
    )
    
    pending_orders = get_pending_orders()
    if not pending_orders:
        return

    for order in pending_orders:
        order_id = order[0]
        # Формируем текст заявки
        text = (f"🔔 НОВАЯ ЗАЯВКА #{order_id}\n\n"
                f"📌 Тип ТС: {order[2]}\n🏭 Марка: {order[3]}\n🔧 Модель: {order[4]}\n"
                f"📅 Год: {order[5]}\n⚡ Мощность: {order[6]}\n🔢 Серийник: {order[7] or 'Отсутствует'}\n"
                f"👤 ФИО: {order[8]}\n🆔 Паспорт: {order[9]}\n🏠 Адрес: {order[10]}\n"
                f"📱 Телефон: {order[11]}\n💨 Скорость: {order[12]} км/ч")

        # СОЗДАЁМ ИНЛАЙН-КНОПКИ
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")]
        ])
        
        # Отправляем сообщение с кнопками АДМИНИСТРАТОРУ
        await bot.send_message(ADMIN_ID, text, reply_markup=keyboard)

# ---------- ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ (ВОТ ОН, РАБОЧИЙ!) ----------
@dp.callback_query()
async def handle_admin_actions(call: types.CallbackQuery):
    # Проверяем, что нажавший кнопку - это администратор
    if call.from_user.id != ADMIN_ID:
        await call.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    action, order_id_str = call.data.split("_")
    order_id = int(order_id_str)
    order = get_order(order_id)

    if not order:
        await call.message.edit_text(f"❌ Заявка #{order_id} не найдена.")
        await call.answer()
        return

    if action == "approve":
        update_order_status(order_id, "approved")
        today = datetime.now().strftime("%d.%m.%Y")
        expiry = (datetime.now() + timedelta(days=365)).strftime("%d.%m.%Y")
        
        order_data = {
            "id": order_id,
            "vehicle_type": order[2], "brand": order[3], "model": order[4],
            "year": order[5], "power": order[6], "serial": order[7] if order[7] else "Отсутствует",
            "full_name": order[8], "passport": order[9], "address": order[10],
            "phone": order[11], "speed": order[12],
            "series_rp": f"RP-{order_id:06d}", "doc_id": f"ID-{order_id:06d}",
            "record_number": f"{order_id:06d}", "registry_number": f"KP-{order_id:06d}",
            "doc_hash": f"HASH-{order_id:06d}", "issue_date": today, "expiry_date": expiry,
        }
        
        pdf_path = generate_pdf(order_data)
        with open(pdf_path, "rb") as pdf:
            await bot.send_document(order[1], pdf, caption="✅ Ваш платеж подтверждён! Документы готовы.")
        
        await call.message.edit_text(f"✅ Заявка #{order_id} подтверждена. PDF отправлен.")
        await call.answer("Заявка подтверждена!")

    elif action == "reject":
        update_order_status(order_id, "rejected")
        await bot.send_message(order[1], "❌ Платёж не подтверждён. Свяжитесь с поддержкой.")
        await call.message.edit_text(f"❌ Заявка #{order_id} отклонена.")
        await call.answer("Заявка отклонена.")

# ---------- ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (РЕФЕРАЛКА, ПОДДЕРЖКА) ----------
@dp.message(F.text == "Заработай с нами/реферальная система")
async def referral(message: types.Message):
    # ... (ваш старый код рефералки)
    user = get_user(message.from_user.id)
    if user:
        text = (f"💰 Мой кабинет RidePass\n\nБаланс: {user[2]} ₽\nВсего заработано: {user[3]} ₽\nРефералов: {user[4]}\n"
                f"Оплаченных заявок рефералов: {user[5]}\nТекущая ставка: 20%\n\n🔗 Ваша реферальная ссылка:\n{user[1]}")
        await message.answer(text, reply_markup=main_menu)

@dp.message(F.text == "Связь с поддержкой")
async def support(message: types.Message):
    await message.answer("📞 Связь с поддержкой\n\nОткрыть чат с менеджером: @ridepass_support", reply_markup=main_menu)

# ---------- ЗАПУСК ----------
async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(start_web_server())
    print("🤖 Бот RidePass успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
