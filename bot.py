import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database import init_db, add_user, add_order, get_order, update_order_status, get_pending_orders, get_user, update_user_balance
from image_filler import generate_pdf

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("No BOT_TOKEN found")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)

# Клавиатуры
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Получить документы")],
        [KeyboardButton(text="Заработай с нами / реферальная система")],
        [KeyboardButton(text="Связь с поддержкой")]
    ],
    resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]],
    resize_keyboard=True
)

# Состояния FSM
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = int(args[1].split("_")[1])
    
    user_id = message.from_user.id
    referral_link = f"https://t.me/{bot.username}?start=ref_{user_id}"
    add_user(user_id, referral_link)
    
    if referrer_id:
        update_user_balance(referrer_id, 500)
        await bot.send_message(referrer_id, "Вам начислено 500₽ за приглашённого друга!")
    
    await message.answer(
        "Добро пожаловать в RidePass\n\nОформление документов на электротранспорт — быстро, удобно и полностью онлайн.\n\nКак получить документы:\n1. Нажмите «Получить документы»\n2. Выберите тип транспортного средства\n3. Укажите данные\n4. Оплатите фиксированную стоимость по реквизитам\n5. Нажмите «Я оплатил»\n6. Дождитесь подтверждения менеджера\n7. Получите готовый PDF-документ прямо в боте",
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
        await message.answer("5. Выберите мощность:\n\n249w - если нет прав категории M1\n3000w - если есть права категории M1", reply_markup=kb)

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
        await message.answer("6. Введите идентификационный номер (номер рамы/мотора):", reply_markup=kb)

@dp.message(Form.custom_power)
async def process_custom_power(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.power)
        await message.answer("5. Выберите мощность:", reply_markup=back_button)
    else:
        await state.update_data(power=message.text + " Вт")
        await state.set_state(Form.serial)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отсутствует")], [KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("6. Введите идентификационный номер (номер рамы/мотора):", reply_markup=kb)

@dp.message(Form.serial)
async def process_serial(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.power)
        await message.answer("5. Выберите мощность:", reply_markup=back_button)
    else:
        serial = "" if message.text == "Отсутствует" else message.text
        await state.update_data(serial=serial)
        await state.set_state(Form.full_name)
        await message.answer("7. Введите ваше ФИО (как в паспорте):", reply_markup=back_button)

@dp.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.serial)
        await message.answer("6. Введите идентификационный номер:", reply_markup=back_button)
    else:
        await state.update_data(full_name=message.text)
        await state.set_state(Form.passport)
        await message.answer("8. Введите серию и номер паспорта:", reply_markup=back_button)

@dp.message(Form.passport)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.full_name)
        await message.answer("7. Введите ваше ФИО:", reply_markup=back_button)
    else:
        await state.update_data(passport=message.text)
        await state.set_state(Form.address)
        await message.answer("9. Введите адрес регистрации:", reply_markup=back_button)

@dp.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.passport)
        await message.answer("8. Введите серию и номер паспорта:", reply_markup=back_button)
    else:
        await state.update_data(address=message.text)
        await state.set_state(Form.phone)
        await message.answer("10. Введите номер телефона (пример: 9991234567):", reply_markup=back_button)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.address)
        await message.answer("9. Введите адрес регистрации:", reply_markup=back_button)
    else:
        await state.update_data(phone=message.text)
        await state.set_state(Form.speed)
        await message.answer("11. Введите максимальную скорость (км/ч):", reply_markup=back_button)

@dp.message(Form.speed)
async def process_speed(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(Form.phone)
        await message.answer("10. Введите номер телефона:", reply_markup=back_button)
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
            "Для оформления заявки оплатите услугу.\n\nСумма: 2499 рублей\nРеквизиты: СБП 89162140001 Т-Банк / Карта 2200700614783958\n\nПосле оплаты нажмите кнопку «Я оплатил».",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Я оплатил")], [KeyboardButton(text="Назад")]],
                resize_keyboard=True
            )
        )
        await state.clear()

@dp.message(F.text == "Я оплатил")
async def i_paid(message: types.Message):
    await message.answer("Спасибо! Мы отправили администраторам уведомление о платеже. Дождитесь подтверждения.", reply_markup=main_menu)
    
    # Отправляем менеджеру
    pending = get_pending_orders()
    for order in pending:
        order_id = order[0]
        text = f"🔔 Новая заявка #{order_id}\n\n"
        text += f"Тип ТС: {order[2]}\nМарка: {order[3]}\nМодель: {order[4]}\nГод: {order[5]}\nМощность: {order[6]}\nСерийник: {order[7]}\nФИО: {order[8]}\nПаспорт: {order[9]}\nАдрес: {order[10]}\nТелефон: {order[11]}\nСкорость: {order[12]}\n\nСтатус: ожидает подтверждения"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")]
        ])
        
        await bot.send_message(123456789, text, reply_markup=kb)  # Замени 123456789 на ID менеджера

@dp.callback_query()
async def handle_admin(call: types.CallbackQuery):
    data = call.data
    order_id = int(data.split("_")[1])
    action = data.split("_")[0]
    
    if action == "approve":
        order = get_order(order_id)
        update_order_status(order_id, "approved")
        order_data = {
            "id": order_id,
            "vehicle_type": order[2],
            "brand": order[3],
            "model": order[4],
            "year": order[5],
            "power": order[6],
            "serial": order[7],
            "full_name": order[8],
            "passport": order[9],
            "address": order[10],
            "phone": order[11],
            "speed": order[12],
        }
        pdf_path = generate_pdf(order_data)
        with open(pdf_path, "rb") as pdf:
            await bot.send_document(order[1], pdf, caption="✅ Ваш платеж подтвержден. Документы готовы.")
        await call.message.edit_text(f"✅ Заявка #{order_id} подтверждена")
    elif action == "reject":
        update_order_status(order_id, "rejected")
        await bot.send_message(order[1], "❌ Ваш платеж не подтвержден. Свяжитесь с поддержкой.")
        await call.message.edit_text(f"❌ Заявка #{order_id} отклонена")
    
    await call.answer()

@dp.message(F.text == "Заработай с нами / реферальная система")
async def referral(message: types.Message):
    user = get_user(message.from_user.id)
    if user:
        text = f"💰 Мой кабинет RidePass\n\n"
        text += f"Баланс: {user[2]} ₽\n"
        text += f"Всего заработано: {user[3]} ₽\n"
        text += f"Рефералов: {user[4]}\n"
        text += f"Оплаченных заявок рефералов: {user[5]}\n"
        text += f"Текущая ставка: 20%\n\n"
        text += f"🔗 Ваша ссылка: {user[1]}\n\n"
        text += "Отправьте ссылку друзьям. Когда приглашенный оформит документы, вознаграждение появится автоматически."
        await message.answer(text, reply_markup=main_menu)
    else:
        await message.answer("Ошибка", reply_markup=main_menu)

@dp.message(F.text == "Связь с поддержкой")
async def support(message: types.Message):
    await message.answer("📞 Связь с поддержкой: @support_ridepass\nИли напишите на почту: support@ridepass.ru", reply_markup=main_menu)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
