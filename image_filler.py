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

    font_normal = ImageFont.truetype(FONT_PATH, size=42)
    font_large = ImageFont.truetype(FONT_PATH, size=55)

    Y_OFF = 18
    X_VAL = 1050

    # Шапка
    if order_id:
        draw.text((1950, 560 + Y_OFF), str(order_id), fill=(26, 36, 43), font=font_large, anchor="ms")

    # Раздел I
    draw.text((X_VAL, 725 + Y_OFF), str(vehicle_type), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 775 + Y_OFF), "СИМ", fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 825 + Y_OFF), str(brand), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 875 + Y_OFF), str(model), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 925 + Y_OFF), str(year), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 975 + Y_OFF), str(vin), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1025 + Y_OFF), str(power), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1075 + Y_OFF), str(max_speed), fill=(26, 36, 43), font=font_normal, anchor="ls")

    # Раздел II
    draw.text((X_VAL, 1195 + Y_OFF), str(full_name), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1275 + Y_OFF), str(passport), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1355 + Y_OFF), str(address), fill=(26, 36, 43), font=font_normal, anchor="ls")

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path
