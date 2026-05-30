import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.png")

def generate_pdf(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_normal = ImageFont.truetype(FONT_PATH, size=58)
    font_large = ImageFont.truetype(FONT_PATH, size=75)

    Y_OFFSET = 25

    fields = {
        "id": {
            "coords": (1240, 260 + Y_OFFSET),
            "text": str(data.get("id", "")),
            "font": font_large,
            "anchor": "ms"
        },
        "vehicle_type": {
            "coords": (1000, 835 + Y_OFFSET),
            "text": data.get("vehicle_type", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "category": {
            "coords": (1000, 930 + Y_OFFSET),
            "text": "СИМ",
            "font": font_normal,
            "anchor": "ls"
        },
        "brand": {
            "coords": (1000, 1025 + Y_OFFSET),
            "text": data.get("brand", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "model": {
            "coords": (1000, 1120 + Y_OFFSET),
            "text": data.get("model", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "year": {
            "coords": (1000, 1215 + Y_OFFSET),
            "text": str(data.get("year", "")),
            "font": font_normal,
            "anchor": "ls"
        },
        "vin": {
            "coords": (1000, 1310 + Y_OFFSET),
            "text": data.get("vin", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "power": {
            "coords": (1000, 1405 + Y_OFFSET),
            "text": data.get("power", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "max_speed": {
            "coords": (1000, 1500 + Y_OFFSET),
            "text": data.get("max_speed", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "full_name": {
            "coords": (1000, 1720 + Y_OFFSET),
            "text": data.get("full_name", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "passport": {
            "coords": (1000, 1855 + Y_OFFSET),
            "text": data.get("passport", ""),
            "font": font_normal,
            "anchor": "ls"
        },
        "address": {
            "coords": (1000, 1990 + Y_OFFSET),
            "text": data.get("address", ""),
            "font": font_normal,
            "anchor": "ls"
        },
    }

    for config in fields.values():
        if config["text"]:
            draw.text(
                xy=config["coords"],
                text=config["text"],
                fill=(26, 36, 43),
                font=config["font"],
                anchor=config["anchor"]
            )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path
