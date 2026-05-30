import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")  # жирный шрифт
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.png")

def generate_pdf(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 58px = 14pt при 300 DPI
    font = ImageFont.truetype(FONT_PATH, size=58)
    
    # Сдвиг вниз для компенсации базовой линии Pillow
    Y_OFFSET = 22

    # КООРДИНАТЫ (твои, с браузера)
    x = 977
    y_base = 1086

    # Основные поля
    fields = {
        "vehicle_type": (x, y_base + Y_OFFSET),
        "brand": (x, y_base + 195 + Y_OFFSET),
        "model": (x, y_base + 390 + Y_OFFSET),
        "full_name": (x, y_base + 780 + Y_OFFSET),
    }

    # Отрисовка
    draw.text(xy=fields["vehicle_type"], text=data.get("vehicle_type", ""), fill=(0,0,0), font=font, anchor="ls")
    draw.text(xy=fields["brand"], text=data.get("brand", ""), fill=(0,0,0), font=font, anchor="ls")
    draw.text(xy=fields["model"], text=data.get("model", ""), fill=(0,0,0), font=font, anchor="ls")
    draw.text(xy=fields["full_name"], text=data.get("full_name", ""), fill=(0,0,0), font=font, anchor="ls")

    # Сохраняем PDF с правильным DPI
    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path

async def generate_pdf_async(data: dict) -> str:
    return await asyncio.to_thread(generate_pdf, data)
