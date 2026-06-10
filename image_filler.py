import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    if os.path.exists(FONT_PATH):
        page.insert_font(fontname="ari", fontfile=FONT_PATH)
        fontname = "ari"
    else:
        fontname = "helv"

    # Соответствие полей в PDF и данных
    field_mapping = {
        "record_number": f"№{data.get('passport_number', '')}",           # №00073
        "series": data.get('series_code', ''),                            # 2026-AB12
        "entry_number": data.get('entry_number', ''),                     # DP-00073
        "issue_date": str(data.get("issue_date", "")),
        "vehicle_type_vision": str(data.get("vehicle_type_vision", "")),
        "brand": str(data.get("brand", "")),
        "model": str(data.get("model", "")),
        "year": str(data.get("year", "")),
        "frame_number": str(data.get("frame_number", "")),
        "engine_number": str(data.get("engine_number", "")),
        "vehicle_type": "Спортинвентарь",
        "engine_capacity": str(data.get("engine_capacity", "")),
        "strokes": str(data.get("strokes", "")),
        "cooling": str(data.get("cooling", "")),
        "transmission": str(data.get("transmission", "")),
        "fuel_system": str(data.get("fuel_system", "")),
        "front_brake": str(data.get("front_brake", "")),
        "rear_brake": str(data.get("rear_brake", "")),
        "weight": str(data.get("weight", "")),
        "full_name": str(data.get("full_name", "")),
        "passport": str(data.get("passport", "")),
        "address": str(data.get("address", "")),
        "doc_hash": str(data.get("doc_hash", "")),
    }

    # Заполняем поля формы
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            field.update()

    # QR-код (ведёт на проверку по entry_number)
    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    # QR-код в правый верхний угол
    qr_rect = fitz.Rect(1550, 50, 1750, 250)
    page.insert_image(qr_rect, stream=qr_bytes)

    # Удаляем интерактивные поля
    for field in page.widgets():
        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
