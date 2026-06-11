import os
import fitz
import qrcode
import gc
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    print(f"📝 fill_order_template: запуск генерации через растрирование")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # 1. Открываем шаблон формы
    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # Заставляем использовать оригинальные шрифты
    try:
        doc.need_appearances(True)
    except:
        pass

    field_mapping = {
        "record_number": str(data.get('passport_number', '')).replace("№", ""),
        "series": data.get('series_code', ''),
        "entry_number": data.get('entry_number', ''),
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

    # Переменные для перехвата координат верхней шапки
    top_y0, top_y1 = None, None

    # Заполняем поля формы
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            field.update()
            
            if name in ("record_number", "series"):
                top_y0 = field.rect.y0
                top_y1 = field.rect.y1

    # 2. QR-код
    w = float(page.rect.x1)
    y0 = top_y0 if top_y0 is not None else page.rect.y1 * 0.078
    y1 = top_y1 if top_y1 is not None else page.rect.y1 * 0.135
    qr_size = y1 - y0

    qr_rect = fitz.Rect(w - qr_size - (w * 0.05), y0, w - (w * 0.05), y1)

    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. Растрирование с DPI=100
    pix = page.get_pixmap(dpi=100)
    
    # Сохраняем как PDF напрямую
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    pix.save(output_path)
    
    doc.close()
    
    # Очистка памяти
    del pix
    gc.collect()
    
    print(f"✅ Документ сохранен: {output_path}")
    return output_path
