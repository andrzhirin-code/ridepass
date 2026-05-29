import asyncio
import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database import init_db, add_user, add_order, get_order, update_order_status, get_pending_orders, get_user, update_user_balance
from image_filler import generate_pdf

API_TOKEN = os.getenv("8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4")
if not API_TOKEN:
    raise ValueError("5171781123")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)

# ========== КЛАВИАТУРЫ ==========
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Получить документы")],
        [KeyboardButton(text="💰 Заработай с нами"), KeyboardButton(text="📞 Связь с поддержкой")]
    ],
    resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Назад")]],
    resize_keyboard=True
)

# ========== FSM СОСТОЯНИЯ ==========
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

# ========== КОМАНДА /START ==========
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
        "🌟 *Добро пожаловать в RidePass* 🌟\n\n"
        "Оформление документов на электротранспорт — быстро, удобно и полностью онлайн.\n\n"
        "📋 *Как получить документы:*\n"
        "1️⃣ Нажмите «Получить документы»\n"
        "2️⃣ Выберите тип транспортного средства\n"
        "3️⃣ Укажите данные\n"
        "4️⃣ Оплатите фиксированную стоимость по реквизитам\n"
        "5️⃣ Нажмите «Я оплатил»\n"
        "6️⃣ Дождитесь подтверждения менеджера\n"
        "7️⃣ Получите готовый PDF-документ прямо в боте\n\n"
        "⏱ Среднее время обработки — от нескольких минут до 1 часа.\n"
        "🔒 Все данные конфиденциальны.",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# ========== НАЗАД В ГЛАВНОЕ МЕНЮ ==========
@dp.message(F.text == "◀️ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🔙 Вы вернулись в главное меню", reply_markup=main_menu)

# ========== ПОЛУЧИТЬ ДОКУМЕНТЫ ==========
@dp.message(F.text == "📄 Получить документы")
async def get_documents(message: types.Message, state: FSMContext):
    await state.set_state(Form.vehicle_type)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛴 Электро Самокат"), KeyboardButton(text="🚲 Электро Велосипед")],
            [KeyboardButton(text="🛞 Моноколесо"), KeyboardButton(text="🏍 Электро Скутер")],
            [KeyboardButton(text="📌 Другое"), KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("📌 *1. Выберите тип транспортного средства:*", reply_markup=kb, parse_mode="Markdown")

@dp.message(Form.vehicle_type)
async def process_vehicle_type(message: types.Message, state: FSMContext):
    if message.text == "📌 Другое":
        await state.set_state(Form.custom_type)
        await message.answer("✏️ Укажите тип вашего ТС:", reply_markup=back_button)
    elif message.text == "◀️ Назад":
        await back_to_menu(message, state)
    else:
        await state.update_data(vehicle_type=message.text.replace("🛴 ", "").replace("🚲 ", "").replace("🛞 ", "").replace("🏍 ", ""))
        await state.set_state(Form.brand)
        await message.answer("📝 *2. Введите марку вашего транспортного средства:*", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.custom_type)
async def process_custom_type(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await get_documents(message, state)
    else:
        await state.update_data(vehicle_type=message.text)
        await state.set_state(Form.brand)
        await message.answer("📝 *2. Введите марку вашего транспортного средства:*", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.brand)
async def process_brand(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await get_documents(message, state)
    else:
        await state.update_data(brand=message.text)
        await state.set_state(Form.model)
        await message.answer("🔧 *3. Введите модель транспортного средства:*\nПример: M365 Pro", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.brand)
        await message.answer("📝 *2. Введите марку транспортного средства:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(model=message.text)
        await state.set_state(Form.year)
        await message.answer("📅 *4. Введите год выпуска:*\nПример: 2024", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.model)
        await message.answer("🔧 *3. Введите модель транспортного средства:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(year=message.text)
        await state.set_state(Form.power)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⚡ 249w"), KeyboardButton(text="⚡ 3000w")],
                [KeyboardButton(text="✏️ Указать свою"), KeyboardButton(text="◀️ Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "⚙️ *5. Выберите мощность двигателя:*\n\n"
            "🔹 *249w* — если нет прав категории M1\n"
            "🔹 *3000w* — если есть права категории M1\n\n"
            "Или нажмите «Указать свою»",
            reply_markup=kb,
            parse_mode="Markdown"
        )

@dp.message(Form.power)
async def process_power(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.year)
        await message.answer("📅 *4. Введите год выпуска:*", reply_markup=back_button, parse_mode="Markdown")
    elif message.text == "✏️ Указать свою":
        await state.set_state(Form.custom_power)
        await message.answer("✏️ Введите мощность в Ваттах (только число):", reply_markup=back_button)
    else:
        await state.update_data(power=message.text.replace("⚡ ", ""))
        await state.set_state(Form.serial)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отсутствует")], [KeyboardButton(text="◀️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("🔢 *6. Введите идентификационный номер (номер рамы/мотора):*\nЕсли номера нет — нажмите «Отсутствует»", reply_markup=kb, parse_mode="Markdown")

@dp.message(Form.custom_power)
async def process_custom_power(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.power)
        await message.answer("⚙️ *5. Выберите мощность двигателя:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(power=message.text)
        await state.set_state(Form.serial)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отсутствует")], [KeyboardButton(text="◀️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("🔢 *6. Введите идентификационный номер (номер рамы/мотора):*", reply_markup=kb, parse_mode="Markdown")

@dp.message(Form.serial)
async def process_serial(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.power)
        await message.answer("⚙️ *5. Выберите мощность двигателя:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        serial = "" if message.text == "❌ Отсутствует" else message.text
        await state.update_data(serial=serial)
        await state.set_state(Form.full_name)
        await message.answer("👤 *7. Введите ваше ФИО полностью (как в паспорте):*", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.serial)
        await message.answer("🔢 *6. Введите идентификационный номер:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(full_name=message.text)
        await state.set_state(Form.passport)
        await message.answer("🆔 *8. Введите серию и номер паспорта:*\nПример: 4510 123456", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.passport)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.full_name)
        await message.answer("👤 *7. Введите ваше ФИО:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(passport=message.text)
        await state.set_state(Form.address)
        await message.answer("🏠 *9. Введите адрес регистрации:*\nПример: г. Москва, ул. Примерная, д. 1, кв. 1", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.passport)
        await message.answer("🆔 *8. Введите серию и номер паспорта:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(address=message.text)
        await state.set_state(Form.phone)
        await message.answer("📱 *10. Введите номер телефона:*\nПример: 9991234567 или +7 999 123-45-67", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.address)
        await message.answer("🏠 *9. Введите адрес регистрации:*", reply_markup=back_button, parse_mode="Markdown")
    else:
        await state.update_data(phone=message.text)
        await state.set_state(Form.speed)
        await message.answer("💨 *11. Введите максимальную скорость (км/ч):*\nПример: 25", reply_markup=back_button, parse_mode="Markdown")

@dp.message(Form.speed)
async def process_speed(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.set_state(Form.phone)
        await message.answer("📱 *10. Введите номер телефона:*", reply_markup=back_button, parse_mode="Markdown")
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
            data.get('serial'),
            data.get('full_name'),
            data.get('passport'),
            data.get('address'),
            data.get('phone'),
            data.get('speed')
        ))
        
        update_order_status(order_id, "waiting_confirm")
        
        await message.answer(
            "💳 *Для оформления заявки оплатите услугу*\n\n"
            "💰 *Сумма:* 2499 рублей\n"
            "🏦 *Реквизиты:*\n"
            "• СБП: +7 916 214-00-01 (Т-Банк)\n"
            "• Карта: 2200 7006 1478 3958\n\n"
            "✅ *После оплаты нажмите кнопку «Я оплатил»*",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="✅ Я оплатил")], [KeyboardButton(text="◀️ Назад")]],
                resize_keyboard=True
            ),
            parse_mode="Markdown"
        )
        await state.clear()

@dp.message(F.text == "✅ Я оплатил")
async def i_paid(message: types.Message):
    await message.answer(
        "🙏 *Спасибо!* Мы отправили администраторам уведомление о платеже.\n\n"
        "⏳ Дождитесь подтверждения. Обычно это занимает от нескольких минут до 1 часа.\n"
        "📄 Как только менеджер проверит оплату — PDF-документ придёт сюда.",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )
    
    pending = get_pending_orders()
    MANAGER_ID = int(os.getenv("MANAGER_ID", "123456789"))
    
    for order in pending:
        order_id = order[0]
        text = (
            f"🔔 *НОВАЯ ЗАЯВКА #{order_id}*\n\n"
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
            f"💨 Скорость: {order[12]} км/ч\n\n"
            f"⏳ Статус: ожидает подтверждения"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")]
        ])
        
        await bot.send_message(MANAGER_ID, text, reply_markup=kb, parse_mode="Markdown")

# ========== КОЛБЭК ДЛЯ АДМИНА ==========
@dp.callback_query()
async def handle_admin(call: types.CallbackQuery):
    data = call.data
    order_id = int(data.split("_")[1])
    action = data.split("_")[0]
    
    if action == "approve":
        order = get_order(order_id)
        update_order_status(order_id, "approved")
        
        today = datetime.now().strftime("%d.%m.%Y")
        expiry = (datetime.now() + timedelta(days=365)).strftime("%d.%m.%Y")
        
        order_data = {
            "id": order_id,
            "vehicle_type": order[2],
            "brand": order[3],
            "model": order[4],
            "year": order[5],
            "power": order[6],
            "serial": order[7] if order[7] else "Отсутствует",
            "full_name": order[8],
            "passport": order[9],
            "address": order[10],
            "phone": order[11],
            "speed": order[12],
            "series_rp": f"RP-{order_id:06d}",
            "doc_id": f"ID-{order_id:06d}",
            "record_number": f"{order_id:06d}",
            "registry_number": f"KP-{order_id:06d}",
            "doc_hash": f"HASH-{order_id:06d}",
            "issue_date": today,
            "expiry_date": expiry,
        }
        
        pdf_path = generate_pdf(order_data)
        with open(pdf_path, "rb") as pdf:
            await bot.send_document(
                order[1],
                pdf,
                caption="✅ *Ваш платеж подтверждён!* Документы готовы.\n\nСпасибо, что выбрали RidePass! 🚀",
                parse_mode="Markdown"
            )
        await call.message.edit_text(f"✅ *Заявка #{order_id} подтверждена*", parse_mode="Markdown")
        
    elif action == "reject":
        update_order_status(order_id, "rejected")
        await bot.send_message(
            order[1],
            "❌ *К сожалению, ваш платёж не подтверждён.*\n\n"
            "Пожалуйста, свяжитесь с поддержкой для уточнения деталей: @ridepass_support",
            parse_mode="Markdown"
        )
        await call.message.edit_text(f"❌ *Заявка #{order_id} отклонена*", parse_mode="Markdown")
    
    await call.answer()

# ========== ЗАРАБОТАЙ С НАМИ ==========
@dp.message(F.text == "💰 Заработай с нами")
async def referral(message: types.Message):
    user = get_user(message.from_user.id)
    if user:
        text = (
            "💰 *МОЙ КАБИНЕТ RIDEPASS*\n\n"
            f"💎 *Баланс:* {user[2]} ₽\n"
            f"📈 *Всего заработано:* {user[3]} ₽\n"
            f"👥 *Рефералов:* {user[4]}\n"
            f"✅ *Оплаченных заявок:* {user[5]}\n"
            f"🎯 *Текущая ставка:* 20%\n\n"
            f"🔗 *Ваша реферальная ссылка:*\n`{user[1]}`\n\n"
            "📢 Отправьте ссылку друзьям!\n"
            "Когда приглашённый пользователь оформит и оплатит документы — "
            "вознаграждение (20% от платежа) автоматически появится в вашем кабинете."
        )
        await message.answer(text, reply_markup=main_menu, parse_mode="Markdown")
    else:
        await message.answer("❌ Ошибка загрузки данных", reply_markup=main_menu)

# ========== СВЯЗЬ С ПОДДЕРЖКОЙ ==========
@dp.message(F.text == "📞 Связь с поддержкой")
async def support(message: types.Message):
    await message.answer(
        "📞 *СВЯЗЬ С ПОДДЕРЖКОЙ*\n\n"
        "👨‍💻 Напишите нашему менеджеру:\n"
        "• Telegram: @ridepass_support\n"
        "• Email: support@ridepass.ru\n\n"
        "🕒 Время ответа: обычно в течение 15 минут",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# ========== ЗАПУСК ==========
async def main():
    init_db()
    print("🤖 Бот RidePass запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
