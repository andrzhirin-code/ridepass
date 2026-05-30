import os
import fitz
import asyncio
from aiogram import Bot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
ADMIN_ID = 5171781123
API_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"

bot = Bot(token=API_TOKEN)

async def send_debug_message(text: str):
    await bot.send_message(ADMIN_ID, text)

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    widgets = list(page.widgets())
    msg = f"Найдено виджетов: {len(widgets)}\n"
    for w in widgets:
        msg += f"Поле: {w.field_name}\n"

    # Отправляем диагностику в Telegram
    asyncio.create_task(send_debug_message(msg))

    output_path = os.path.join(BASE_DIR, f"debug.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
