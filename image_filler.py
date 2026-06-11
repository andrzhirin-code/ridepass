import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    print(f"📝 fill_order_template вызван (безопасный векторный режим)")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # Открываем документ и загружаем первую страницу
    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    try:
        doc.need_appearances(True)
    except:
        pass

    if os.path.exists(FONT_PATH):
        page.insert_font(fontname="ari", fontfile=FONT_PATH)

    field_mapping = {
        "record_number": f"№{data.get('passport_number', '')}",
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

    # Генерация QR-кода
    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    qr = qrcode.QRCode(box_size=20, border=4)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    qr_rect = fitz.Rect(1550, 200, 1750, 400)
    page.insert_image(qr_rect, stream=qr_bytes)

    # ГЛАВНОЕ: ЭТОТ БЛОК ЭКОНОМИТ ПАМЯТЬ
    # Конвертируем в "плоский" PDF (поля исчезают, память не тратится)
    result = doc.convert_to_pdf()
    flattened_bytes = result if isinstance(result, bytes) else result[2]
    doc.close()

    # Сохраняем результат
    final_doc = fitz.open("pdf", flattened_bytes)
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    final_doc.save(output_path, garbage=4, deflate=True)
    final_doc.close()
    
    print(f"✅ PDF сохранен: {output_path}")
    return output_path
