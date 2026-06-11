import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    print(f"📝 fill_order_template: запуск генерации защищенного документа")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # 1. Открываем шаблон формы
    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # Принудительно заставляем использовать оригинальные шрифты
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

    # Заполняем поля формы
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            field.update()

    # 2. ИДЕАЛЬНАЯ СИММЕТРИЯ QR-КОДА
    w = float(page.rect.x1)
    qr_rect = fitz.Rect(w - 350, 200, w - 150, 400)

    # ИСПРАВЛЕНИЕ: правильная ссылка
    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. ЖЕЛЕЗОБЕТОННЫЙ ФЛАТТЕНИНГ БЕЗ НАГРУЗКИ НА ОЗУ
    # Удаляем интерактивные поля, текст становится частью бланка
    for field in page.widgets():
        page.delete_widget(field)

    # Сохраняем финальный защищенный векторный файл
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    
    print(f"✅ Ультра-легкий невыделяемый ПТС успешно сохранен: {output_path}")
    return output_path
