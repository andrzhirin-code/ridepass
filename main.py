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

from database import init_db, add_user, add_order, get_order, update_order_status, get_pending_orders, get_user, update_user_balance, generate_unique_number, generate_doc_hash
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

# ========== FSM (ВСЕ ПОЛЯ) ==========
class Form(StatesGroup):
    vehicle_type_vision = State()  # Вид техники
    brand = State()                # Марка
    model = State()                # Модель
    year = State()                 # Год выпуска
    frame_number = State()         # Номер рамы
    engine_number = State()        # Номер двигателя
    engine_capacity = State()      # Объем двигателя
    strokes = State()              # Количество тактов
    cooling = State()              # Охлаждение
    transmission = State()         # Коробка передач
    fuel_system = State()          # Топливная система
    front_brake = State()          # Передняя тормозная система
    rear_brake = State()           # Задняя тормозная система
    weight = State()               # Масса без нагрузки
    full_name = State()            # ФИО владельца
    passport = State()             # Паспорт
    address = State()              # Адрес
    phone = State()                # Телефон

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
        "Оформление документов на мототехнику — быстро, удобно и полностью онлайн.\n\n"
        "📋 Как получить документы:\n"
        "1️⃣ Нажмите «Получить документы»\n"
        "2️⃣ Укажите данные\n"
        "3️⃣ Оплатите фиксированную стоимость по реквизитам\n"
        "4️⃣ Нажмите «Я оплатил»\n"
        "5️⃣ Дождитесь подтверждения менеджера\n"
        "6️⃣ Получите готовый PDF-документ прямо в боте",
        reply_markup=main_menu
    )

@dp.message(F.text == "Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu)

@dp.message(F.text == "Получить документы")
async def get_documents(message: types.Message, state: FSMContext):
    await state.set_state(Form.vehicle_type_vision)
    await message.answer("1️⃣ Введите вид техники (например: Квадроцикл, Мотоцикл, Скутер):", reply_markup=back_button)

# ========== ВСЕ ВОПРОСЫ АНКЕТЫ ==========
@dp.message(Form.vehicle_type_vision)
async def process_vehicle_type_vision(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await back_to_menu(message, state)
    else:
        await state.update_data(vehicle_type_vision=message.text)
        await state.set_state(Form.brand)
        await message.answer("2️⃣ Введите марку:", reply_markup=back_button)

@dp.message(Form.brand)
async def process_brand(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.vehicle_type_vision)
        await message.answer("1️⃣ Введите вид техники:", reply_markup=back_button)
    else:
        await state.update_data(brand=message.text)
        await state.set_state(Form.model)
        await message.answer("3️⃣ Введите модель:", reply_markup=back_button)

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.brand)
        await message.answer("2️⃣ Введите марку:", reply_markup=back_button)
    else:
        await state.update_data(model=message.text)
        await state.set_state(Form.year)
        await message.answer("4️⃣ Введите год выпуска:", reply_markup=back_button)

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.model)
        await message.answer("3️⃣ Введите модель:", reply_markup=back_button)
    else:
        await state.update_data(year=message.text)
        await state.set_state(Form.frame_number)
        await message.answer("5️⃣ Введите номер рамы:", reply_markup=back_button)

@dp.message(Form.frame_number)
async def process_frame_number(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.year)
        await message.answer("4️⃣ Введите год выпуска:", reply_markup=back_button)
    else:
        await state.update_data(frame_number=message.text)
        await state.set_state(Form.engine_number)
        await message.answer("6️⃣ Введите номер двигателя:", reply_markup=back_button)

@dp.message(Form.engine_number)
async def process_engine_number(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.frame_number)
        await message.answer("5️⃣ Введите номер рамы:", reply_markup=back_button)
    else:
        await state.update_data(engine_number=message.text)
        await state.set_state(Form.engine_capacity)
        await message.answer("7️⃣ Введите объём двигателя (в куб. см):", reply_markup=back_button)

@dp.message(Form.engine_capacity)
async def process_engine_capacity(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.engine_number)
        await message.answer("6️⃣ Введите номер двигателя:", reply_markup=back_button)
    else:
        await state.update_data(engine_capacity=message.text)
        await state.set_state(Form.strokes)
        await message.answer("8️⃣ Введите количество тактов (2 или 4):", reply_markup=back_button)

@dp.message(Form.strokes)
async def process_strokes(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.engine_capacity)
        await message.answer("7️⃣ Введите объём двигателя:", reply_markup=back_button)
    else:
        await state.update_data(strokes=message.text)
        await state.set_state(Form.cooling)
        await message.answer("9️⃣ Введите тип охлаждения (воздушное/жидкостное):", reply_markup=back_button)

@dp.message(Form.cooling)
async def process_cooling(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.strokes)
        await message.answer("8️⃣ Введите количество тактов:", reply_markup=back_button)
    else:
        await state.update_data(cooling=message.text)
        await state.set_state(Form.transmission)
        await message.answer("🔟 Введите тип коробки передач (механика/автомат/вариатор):", reply_markup=back_button)

@dp.message(Form.transmission)
async def process_transmission(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.cooling)
        await message.answer("9️⃣ Введите тип охлаждения:", reply_markup=back_button)
    else:
        await state.update_data(transmission=message.text)
        await state.set_state(Form.fuel_system)
        await message.answer("1️⃣1️⃣ Введите тип топливной системы (карбюратор/инжектор):", reply_markup=back_button)

@dp.message(Form.fuel_system)
async def process_fuel_system(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.transmission)
        await message.answer("🔟 Введите тип коробки передач:", reply_markup=back_button)
    else:
        await state.update_data(fuel_system=message.text)
        await state.set_state(Form.front_brake)
        await message.answer("1️⃣2️⃣ Введите тип передней тормозной системы (дисковые/барабанные):", reply_markup=back_button)

@dp.message(Form.front_brake)
async def process_front_brake(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.fuel_system)
        await message.answer("1️⃣1️⃣ Введите тип топливной системы:", reply_markup=back_button)
    else:
        await state.update_data(front_brake=message.text)
        await state.set_state(Form.rear_brake)
        await message.answer("1️⃣3️⃣ Введите тип задней тормозной системы (дисковые/барабанные):", reply_markup=back_button)

@dp.message(Form.rear_brake)
async def process_rear_brake(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.front_brake)
        await message.answer("1️⃣2️⃣ Введите тип передней тормозной системы:", reply_markup=back_button)
    else:
        await state.update_data(rear_brake=message.text)
        await state.set_state(Form.weight)
        await message.answer("1️⃣4️⃣ Введите массу без нагрузки (в кг):", reply_markup=back_button)

@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.rear_brake)
        await message.answer("1️⃣3️⃣ Введите тип задней тормозной системы:", reply_markup=back_button)
    else:
        await state.update_data(weight=message.text)
        await state.set_state(Form.full_name)
        await message.answer("1️⃣5️⃣ Введите ваше ФИО полностью:", reply_markup=back_button)

@dp.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.weight)
        await message.answer("1️⃣4️⃣ Введите массу без нагрузки:", reply_markup=back_button)
    else:
        await state.update_data(full_name=message.text)
        await state.set_state(Form.passport)
        await message.answer("1️⃣6️⃣ Введите серию и номер паспорта:", reply_markup=back_button)

@dp.message(Form.passport)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.full_name)
        await message.answer("1️⃣5️⃣ Введите ваше ФИО:", reply_markup=back_button)
    else:
        await state.update_data(passport=message.text)
        await state.set_state(Form.address)
        await message.answer("1️⃣7️⃣ Введите адрес регистрации:", reply_markup=back_button)

@dp.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.passport)
        await message.answer("1️⃣6️⃣ Введите серию и номер паспорта:", reply_markup=back_button)
    else:
        await state.update_data(address=message.text)
        await state.set_state(Form.phone)
        await message.answer("1️⃣8️⃣ Введите номер телефона:\nПример: 9991234567", reply_markup=back_button)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.address)
        await message.answer("1️⃣7️⃣ Введите адрес регистрации:", reply_markup=back_button)
    else:
        await state.update_data(phone=message.text)
        data = await state.get_data()
        
        # Генерируем уникальные номера и хеш
        unique_number = generate_unique_number()
        today = datetime.now().strftime("%d.%m.%Y")
        entry_number = f"DP-{unique_number[1:]}"
        
        # Создаём слепок данных для хеша
        data_snapshot = f"{data.get('brand')}{data.get('model')}{data.get('frame_number')}{data.get('engine_number')}{today}"
        doc_hash = generate_doc_hash(data_snapshot)
        
        # Сохраняем в БД
        order_id = add_order((
            message.from_user.id,
            unique_number,              # unique_doc_number
            doc_hash,                   # doc_hash
            "DP",                       # series
            today,                      # issue_date
            entry_number,               # entry_number
            data.get('vehicle_type_vision'),
            data.get('brand'),
            data.get('model'),
            data.get('year'),
            data.get('frame_number'),
            data.get('engine_number'),
            "Спортинвентарь",           # vehicle_type_static
            data.get('engine_capacity'),
            data.get('strokes'),
            data.get('cooling'),
            data.get('transmission'),
            data.get('fuel_system'),
            data.get('front_brake'),
            data.get('rear_brake'),
            data.get('weight'),
            data.get('full_name'),
            data.get('passport'),
            data.get('address'),
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
            f"📌 № паспорта: {order[2]}\n"
            f"📌 № записи: {order[6]}\n"
            f"🏍 Вид техники: {order[7]}\n"
            f"🏭 Марка: {order[8]}\n"
            f"🔧 Модель: {order[9]}\n"
            f"📅 Год: {order[10]}\n"
            f"🔢 Номер рамы: {order[11]}\n"
            f"🔢 Номер двигателя: {order[12]}\n"
            f"⚡ Объём: {order[14]}\n"
            f"🔄 Тактов: {order[15]}\n"
            f"❄️ Охлаждение: {order[16]}\n"
            f"⚙️ Коробка: {order[17]}\n"
            f"⛽ Топливная: {order[18]}\n"
            f"🛑 Передний тормоз: {order[19]}\n"
            f"🛑 Задний тормоз: {order[20]}\n"
            f"⚖️ Масса: {order[21]}\n"
            f"👤 ФИО: {order[22]}\n"
            f"🆔 Паспорт: {order[23]}\n"
            f"🏠 Адрес: {order[24]}\n"
            f"📱 Телефон: {order[25] if len(order) > 25 else ''}\n"
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
            
            def get_clean(val):
                return str(val) if val is not None else ""
            
            order_data = {
                "record_number": get_clean(order[2]),      # unique_doc_number
                "series": get_clean(order[4]),            # series
                "issue_date": get_clean(order[5]),        # issue_date
                "entry_number": get_clean(order[6]),      # entry_number
                "vehicle_type_vision": get_clean(order[7]),
                "brand": get_clean(order[8]),
                "model": get_clean(order[9]),
                "year": get_clean(order[10]),
                "frame_number": get_clean(order[11]),
                "engine_number": get_clean(order[12]),
                "engine_capacity": get_clean(order[14]),
                "strokes": get_clean(order[15]),
                "cooling": get_clean(order[16]),
                "transmission": get_clean(order[17]),
                "fuel_system": get_clean(order[18]),
                "front_brake": get_clean(order[19]),
                "rear_brake": get_clean(order[20]),
                "weight": get_clean(order[21]),
                "full_name": get_clean(order[22]),
                "passport": get_clean(order[23]),
                "address": get_clean(order[24]),
                "doc_hash": get_clean(order[3]),          # doc_hash
            }
            
            pdf_path = await asyncio.to_thread(fill_order_template, order_data)
            document = FSInputFile(pdf_path)
            await bot.send_document(order[1], document, caption="✅ Ваш платеж подтверждён! Паспорт мототехники готов.")
            
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            await callback.message.edit_text(f"✅ Заявка #{order_id} подтверждена. Документ отправлен.")
            
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
    
    # Healthcheck для cron-job.org
    app.router.add_get("/ping", lambda request: web.Response(text="OK"))
    
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
