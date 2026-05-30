import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.png")

def fill_order_template(
    order_id: str,
    vehicle_type: str,
    brand: str,
    model: str,
    year: str,
    vin: str,
    power: str,
    max_speed: str,
    full_name: str,
    passport: str,
    address: str
) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")
        
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_normal = ImageFont.truetype(FONT_PATH, size=45)
    font_large = ImageFont.truetype(FONT_PATH, size=60)
    font_debug = ImageFont.truetype(FONT_PATH, size=24)

    # ========== ОТЛАДОЧНАЯ СЕТКА ==========
    # Синие линии каждые 100 пикселей с подписями Y
    for y in range(0, img.height, 100):
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 255, 100), width=1)
        draw.text((20, y + 5), f"Y: {y}", fill=(0, 0, 255), font=font_debug)
    # Вертикальные линии для X
    for x in range(0, img.width, 100):
        draw.line([(x, 0), (x, img.height)], fill=(0, 255, 0, 100), width=1)
        draw.text((x + 5, 20), f"X: {x}", fill=(0, 255, 0), font=font_debug)
    # ====================================

    Y_OFF = 20
    X_VAL = 1080

    # Шапка
    if order_id:
        draw.text((1950, 560 + Y_OFF), str(order_id), fill=(26, 36, 43), font=font_large, anchor="ms")

    # Раздел I
    draw.text((X_VAL, 1475 + Y_OFF), str(vehicle_type), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1570 + Y_OFF), "СИМ", fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1665 + Y_OFF), str(brand), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1760 + Y_OFF), str(model), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1855 + Y_OFF), str(year), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1950 + Y_OFF), str(vin), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 2045 + Y_OFF), str(power), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 2140 + Y_OFF), str(max_speed), fill=(26, 36, 43), font=font_normal, anchor="ls")

    # Раздел II
    draw.text((X_VAL, 2370 + Y_OFF), str(full_name), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 2515 + Y_OFF), str(passport), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 2660 + Y_OFF), str(address), fill=(26, 36, 43), font=font_normal, anchor="ls")

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path
