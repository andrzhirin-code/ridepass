import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "timesbd.ttf")

def fill_order_template(data: dict) -> str:
    print("📝 fill_order_template: старт")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"⚠️ Файл шрифта timesbd.ttf не найден! Загрузите его в папку проекта.")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # 1. РЕГИСТРИРУЕМ ВНЕШНИЙ ШРИФТ
    font_name = "TimesNewRomanBold"
    page.insert_font(fontname=font_name, fontfile=FONT_PATH)

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

    # 2. ЧИТАЕМ КООРДИНАТЫ ПОЛЕЙ И РИСУЕМ ТЕКСТ
    widgets_to_remove = []
    
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            text_to_print = field_mapping[name]
            rect = field.rect
            
            # Автоматический размер шрифта
            font_size = rect.height * 0.75
            
            point = fitz.Point(rect.x0 + 2, rect.y1 - 3)
            
            page.insert_text(
                point, 
                text_to_print, 
                fontname=font_name, 
                fontsize=font_size,
                color=(0, 0, 0)
            )
            
            widgets_to_remove.append(field)
    
    # Удаляем интерактивные поля
    for field in widgets_to_remove:
        page.delete_widget(field)

    # QR-код
    w = float(page.rect.x1)
    qr_rect = fitz.Rect(w - 250, 200, w - 50, 400)
    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. ЗАЩИТА ОТ ВЫДЕЛЕНИЯ И КОПИРОВАНИЯ
    perm_mask = fitz.PDF_PERM_ACCESSIBILITY 

    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    doc.save(
        output_path, 
        garbage=4, 
        deflate=True, 
        encryption=fitz.PDF_ENCRYPT_AES_256, 
        owner_pw=os.urandom(16).hex(), 
        permissions=perm_mask
    )
    doc.close()
    
    print(f"✅ Документ успешно сгенерирован и аппаратно заблокирован: {output_path}")
    return output_path
