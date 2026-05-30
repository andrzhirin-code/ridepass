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

    # Координаты от Gemini (X=1080, Y с учетом Y_OFFSET)
    fields = {
        "id":           {"coords": (1240, 285), "font_type": "large", "anchor": "ms"},
        "vehicle_type": {"coords": (1080, 860), "font_type": "normal", "anchor": "ls"},
        "category":     {"coords": (1080, 955), "font_type": "normal", "anchor": "ls"},
        "brand":        {"coords": (1080, 1050), "font_type": "normal", "anchor": "ls"},
        "model":        {"coords": (1080, 1145), "font_type": "normal", "anchor": "ls"},
        "year":         {"coords": (1080, 1240), "font_type": "normal", "anchor": "ls"},
        "vin":          {"coords": (1080, 1335), "font_type": "normal", "anchor": "ls"},
        "power":        {"coords": (1080, 1430), "font_type": "normal", "anchor": "ls"},
        "max_speed":    {"coords": (1080, 1525), "font_type": "normal", "anchor": "ls"},
        "full_name":    {"coords": (1080, 1745), "font_type": "normal", "anchor": "ls"},
        "passport":     {"coords": (1080, 1880), "font_type": "normal", "anchor": "ls"},
        "address":      {"coords": (1080, 2015), "font_type": "normal", "anchor": "ls"},
    }

    for field_name, config in fields.items():
        # Категория всегда "СИМ"
        if field_name == "category":
            text_value = "СИМ"
        else:
            text_value = str(data.get(field_name, ""))
        
        if not text_value or text_value == "None":
            continue

        current_font = font_large if config["font_type"] == "large" else font_normal

        draw.text(
            xy=config["coords"],
            text=text_value,
            fill=(15, 25, 35),
            font=current_font,
            anchor=config["anchor"]
        )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path
