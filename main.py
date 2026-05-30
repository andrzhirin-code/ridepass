import asyncio
import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, FSInputFile
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from database import init_db, add_user, add_order, get_order, update_order_status, get_pending_orders, get_user, update_user_balance
from image_filler import fill_order_template

API_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"
ADMIN_ID = 5171781123

PORT = int(os.getenv("PORT", 10000))
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://ridepass.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)

# ========== КЛАВИАТУРЫ ==========
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

# ========== FSM ==========
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

# ========== СТАРТ ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
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
        "🌟 Добро пожаловать в RidePass 🌟\n\n"
        "Оформление документов на электротранспорт — быстро, удобно и полностью онлайн.\n\n"
        "📋 Как получить документы:\n"
        "1️⃣ Нажмите «Получить документы»\n"
        "2️⃣ Выберите тип транспортного средства\n"
        "3️⃣ Укажите данные\n"
        "4️⃣ Оплатите фиксированную стоимость по реквизитам\n"
        "5️⃣ Нажмите «Я оплатил»\n"
        "6️⃣ Дождитесь подтверждения менеджера\n"
        "7️⃣ Получите готовый PDF-документ прямо в боте",
        reply_markup=main_menu
    )

@dp.message(F.text == "Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu)

@dp.message(F.text == "Получить документы")
async def get_documents(message: types.Message, state: FSMContext):
    await state.set_state(Form.vehicle_type)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Электро Самокат"), KeyboardButton(text="Электро Велосипед")],
            [KeyboardButton(text="Моноколесо"), KeyboardButton(text="Электро Скутер")],
            [KeyboardButton(text="Другое"), KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("1. Выберите тип Транспортного средства:", reply_markup=kb)

@dp.message(Form.vehicle_type)
async def process_vehicle_type(message: types.Message, state: FSMContext):
    if message.text == "Другое":
        await state.set_state(Form.custom_type)
        await message.answer("Укажите тип вашего ТС:", reply_markup=back_button)
    elif message.text == "Назад":
        await back_to_menu(message, state)
    else:
        await state.update_data(vehicle_type=message.text)
        await state.set_state(Form.brand)
        await message.answer("2. Введите марку вашего Транспортного средства:", reply_markup=back_button)

@dp.message(Form.custom_type)
async def process_custom_type(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await get_documents(message, state)
    else:
        await state.update_data(vehicle_type=message.text)
        await state.set_state(Form.brand)
        await message.answer("2. Введите марку вашего Транспортного средства:", reply_markup=back_button)

@dp.message(Form.brand)
async def process_brand(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await get_documents(message, state)
    else:
        await state.update_data(brand=message.text)
        await state.set_state(Form.model)
        await message.answer("3. Введите модель вашего Транспортного средства:", reply_markup=back_button)

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.brand)
        await message.answer("2. Введите марку вашего Транспортного средства:", reply_markup=back_button)
    else:
        await state.update_data(model=message.text)
        await state.set_state(Form.year)
        await message.answer("4. Введите год выпуска:", reply_markup=back_button)

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.model)
        await message.answer("3. Введите модель вашего Транспортного средства:", reply_markup=back_button)
    else:
        await state.update_data(year=message.text)
        await state.set_state(Form.power)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="249w"), KeyboardButton(text="3000w")],
                [KeyboardButton(text="Указать свою"), KeyboardButton(text="Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "5. Выберите желаемую мощность вашего Транспортного Средства:\n\n"
            "Если у вас нет водительского удостоверения с категорией М1 — выбирайте 249w.\n"
            "Если у вас есть водительское удостоверение с категорией М1 — выбирайте 3000w.\n"
            "Если нужна другая мощность — нажмите «Указать свою».",
            reply_markup=kb
        )

@dp.message(Form.power)
async def process_power(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.year)
        await message.answer("4. Введите год выпуска:", reply_markup=back_button)
    elif message.text == "Указать свою":
        await state.set_state(Form.custom_power)
        await message.answer("Введите мощность в Ваттах:", reply_markup=back_button)
    else:
        await state.update_data(power=message.text)
        await state.set_state(Form.serial)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отсутствует")], [KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("6. Введите идентификационный номер вашего Транспортного средства (номер рамы/мотора и т.д.):\n\nЕсли такого номера нет, нажмите «Отсутствует».", reply_markup=kb)

@dp.message(Form.custom_power)
async def process_custom_power(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.power)
        await message.answer("5. Выберите желаемую мощность:", reply_markup=back_button)
    else:
        await state.update_data(power=message.text)
        await state.set_state(Form.serial)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отсутствует")], [KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("6. Введите идентификационный номер:", reply_markup=kb)

@dp.message(Form.serial)
async def process_serial(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.power)
        await message.answer("5. Выберите желаемую мощность:", reply_markup=back_button)
    else:
        serial = "" if message.text == "Отсутствует" else message.text
        await state.update_data(serial=serial)
        await state.set_state(Form.full_name)
        await message.answer("7. Введите ваше ФИО, которое будет указано в документе как «собственник»:", reply_markup=back_button)

@dp.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.serial)
        await message.answer("6. Введите идентификационный номер:", reply_markup=back_button)
    else:
        await state.update_data(full_name=message.text)
        await state.set_state(Form.passport)
        await message.answer("8. Введите серию и номер вашего Паспорта:", reply_markup=back_button)

@dp.message(Form.passport)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.full_name)
        await message.answer("7. Введите ваше ФИО:", reply_markup=back_button)
    else:
        await state.update_data(passport=message.text)
        await state.set_state(Form.address)
        await message.answer("9. Введите адрес вашего проживания:", reply_markup=back_button)

@dp.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.passport)
        await message.answer("8. Введите серию и номер Паспорта:", reply_markup=back_button)
    else:
        await state.update_data(address=message.text)
        await state.set_state(Form.phone)
        await message.answer("10. Введите номер телефона владельца:\n\nМожно написать без +7 — бот добавит автоматически.\nПример: 9991234567", reply_markup=back_button)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.address)
        await message.answer("9. Введите адрес вашего проживания:", reply_markup=back_button)
    else:
        await state.update_data(phone=message.text)
        await state.set_state(Form.speed)
        await message.answer("11. Введите максимальную скорость (км/ч):", reply_markup=back_button)

@dp.message(Form.speed)
async def process_speed(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.phone)
        await message.answer("10. Введите номер телефона владельца:", reply_markup=back_button)
    else:
        await state.update_data(speed=message.text)
        data = await state.get_data()
        
        order_id = add_order((
            message.from_user.id,
            data.get('vehicle_type'),
            data.get('brand'),
            data.get('model'),
            data.get('year'),
            data.get('power'),
            data.get('serial', ''),
            data.get('full_name'),
            data.get('passport'),
            data.get('address'),
            data.get('phone'),
            data.get('speed')
        ))
        
        update_order_status(order_id, "waiting_confirm")
        
        await message.answer(
            "💳 Для оформления заявки оплатите услугу\n\n"
            "💰 Сумма: 2499 рублей\n"
            "🏦 Реквизиты для оплаты:\n"
            "• СБП: +7 916 214-00-01 (Т-Банк)\n"
            "• Карта: 2200 7006 1478 3958\n\n"
            "✅ После оплаты нажмите кнопку «Я оплатил»",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Я оплатил")], [KeyboardButton(text="Назад")]],
                resize_keyboard=True
            )
        )
        await state.clear()

@dp.message(F.text == "Я оплатил")
async def i_paid(message: types.Message):
    await message.answer(
        "🙏 Спасибо! Мы отправили администраторам уведомление о платеже.\n\n"
        "⏳ Дождитесь подтверждения.",
        reply_markup=main_menu
    )
    
    pending = get_pending_orders()
    
    for order in pending:
        order_id = order[0]
        text = (
            f"🔔 НОВАЯ ЗАЯВКА #{order_id}\n\n"
            f"📌 Тип ТС: {order[2]}\n"
            f"🏭 Марка: {order[3]}\n"
            f"🔧 Модель: {order[4]}\n"
            f"📅 Год: {order[5]}\n"
            f"⚡ Мощность: {order[6]}\n"
            f"🔢 Серийник: {order[7] if order[7] else 'Отсутствует'}\n"
            f"👤 ФИО: {order[8]}\n"
            f"🆔 Паспорт: {order[9]}\n"
            f"🏠 Адрес: {order[10]}\n"
            f"📱 Телефон: {order[11]}\n"
            f"💨 Скорость: {order[12]} км/ч"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")]
        ])
        
        await bot.send_message(ADMIN_ID, text, reply_markup=kb)

# ========== ОБРАБОТЧИК КНОПОК ==========
@dp.callback_query()
async def handle_admin(callback: CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.message.answer("У вас нет прав")
        return
    
    action, order_id_str = callback.data.split("_")
    order_id = int(order_id_str)
    order = get_order(order_id)
    
    if not order:
        await callback.message.edit_text(f"❌ Заявка #{order_id} не найдена")
        return
    
    if action == "approve":
        try:
            today = datetime.now().strftime("%d.%m.%Y")
            expiry = (datetime.now() + timedelta(days=365)).strftime("%d.%m.%Y")
            
            # ЯВНОЕ СОПОСТАВЛЕНИЕ ИНДЕКСОВ (поправь по своим данным)
            pdf_path = await asyncio.to_thread(
                fill_order_template,
                order_id=str(order[0]),
                vehicle_type=str(order[2]),
                brand=str(order[3]),
                model=str(order[4]),
                year=str(order[5]),
                vin=str(order[7]),
                power=str(order[6]),
                max_speed=str(order[12]),
                full_name=str(order[8]),
                passport=str(order[9]),
                address=str(order[10])
            )
            
            document = FSInputFile(pdf_path)
            await bot.send_document(order[1], document, caption="✅ Ваш платеж подтверждён! Документы готовы.")
            
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            await callback.message.edit_text(f"✅ Заявка #{order_id} подтверждена. PDF отправлен.")
            
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {e}")
            
    elif action == "reject":
        update_order_status(order_id, "rejected")
        await bot.send_message(order[1], "❌ Платёж не подтверждён. Свяжитесь с поддержкой.")
        await callback.message.edit_text(f"❌ Заявка #{order_id} отклонена.")

# ========== РЕФЕРАЛКА ==========
@dp.message(F.text == "Заработай с нами/реферальная система")
async def referral(message: types.Message):
    user = get_user(message.from_user.id)
    if user:
        text = (
            f"💰 Мой кабинет RidePass\n\n"
            f"Баланс: {user[2]} ₽\n"
            f"Всего заработано: {user[3]} ₽\n"
            f"Рефералов: {user[4]}\n"
            f"Оплаченных заявок рефералов: {user[5]}\n"
            f"Текущая ставка: 20%\n\n"
            f"🔗 Ваша реферальная ссылка:\n{user[1]}\n\n"
            f"Отправьте ссылку друзьям. Когда приглашенный пользователь оформит и оплатит документы, вознаграждение автоматически появится в вашем кабинете."
        )
        await message.answer(text, reply_markup=main_menu)

# ========== ПОДДЕРЖКА ==========
@dp.message(F.text == "Связь с поддержкой")
async def support(message: types.Message):
    await message.answer(
        "📞 Связь с поддержкой\n\n"
        "Открыть чат с менеджером: @ridepass_support",
        reply_markup=main_menu
    )

# ========== ЗАПУСК ==========
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL, allowed_updates=["message", "callback_query"])
    print(f"Webhook set to {WEBHOOK_URL}")

async def main():
    init_db()
    
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    await on_startup()
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    print(f"🤖 Бот RidePass запущен на порту {PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
