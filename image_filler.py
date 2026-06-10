import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    # Готовим данные для вставки
    values = {
        "record_number": data.get("record_number", ""), # № паспорта мототехники
        "series": data.get("series", ""),               # Серия DP
        "issue_date": data.get("issue_date", ""),       # Дата формирования
        "entry_number": data.get("entry_number", ""),   # № записи
        "vehicle_type_vision": data.get("vehicle_type_vision", ""),
        "brand": data.get("brand", ""),
        "model": data.get("model", ""),
        "year": data.get("year", ""),
        "frame_number": data.get("frame_number", ""),
        "engine_number": data.get("engine_number", ""),
        "vehicle_type": "Спортинвентарь", # Всегда фиксированное значение
        "engine_capacity": data.get("engine_capacity", ""),
        "strokes": data.get("strokes", ""),
        "cooling": data.get("cooling", ""),
        "transmission": data.get("transmission", ""),
        "fuel_system": data.get("fuel_system", ""),
        "front_brake": data.get("front_brake", ""),
        "rear_brake": data.get("rear_brake", ""),
        "weight": data.get("weight", ""),
        "full_name": data.get("full_name", ""),
        "passport": data.get("passport", ""),
        "address": data.get("address", ""),
        "doc_hash": data.get("doc_hash", ""), # Хеш для проверки
    }

    # 1. Заполняем текстовые поля
    for field in page.widgets():
        name = field.field_name
        if name in values and values[name]:
            field.field_value = str(values[name])
            field.update()

    # 2. Генерируем и вставляем QR-код
    verification_url = f"https://ridepass.onrender.com/check?code={values['entry_number']}"
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем QR-код в память
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    # Вставляем QR-код на страницу (координаты X, Y подбери под свой бланк)
    qr_rect = fitz.Rect(500, 50, 500+50, 50+50) # Пример: верхний правый угол
    page.insert_image(qr_rect, stream=qr_bytes)

    doc.save(os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf"))
    doc.close()
