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

    font_normal = ImageFont.truetype(FONT_PATH, size=58)
    font_large = ImageFont.truetype(FONT_PATH, size=75)

    Y_OFF = 25
    X_VAL = 1080

    # Шапка (ID)
    if order_id:
        draw.text((1240, 260 + Y_OFF), str(order_id), fill=(26, 36, 43), font=font_large, anchor="ms")

    # Раздел I (Y от 410 до 795)
    draw.text((X_VAL, 410 + Y_OFF), str(vehicle_type), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 465 + Y_OFF), "СИМ", fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 520 + Y_OFF), str(brand), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 575 + Y_OFF), str(model), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 630 + Y_OFF), str(year), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 685 + Y_OFF), str(vin), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 740 + Y_OFF), str(power), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 795 + Y_OFF), str(max_speed), fill=(26, 36, 43), font=font_normal, anchor="ls")

    # Раздел II (Y от 905 до 1015)
    draw.text((X_VAL, 905 + Y_OFF), str(full_name), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 960 + Y_OFF), str(passport), fill=(26, 36, 43), font=font_normal, anchor="ls")
    draw.text((X_VAL, 1015 + Y_OFF), str(address), fill=(26, 36, 43), font=font_normal, anchor="ls")

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    img.save(output_path, "PDF", resolution=300.0, quality=100)
    return output_path
