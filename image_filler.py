import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # 1. Открываем шаблон формы
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0] # Важно: берем конкретно первую страницу через индекс [0]

    try:
        doc.need_appearances(True)
    except:
        pass

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

    # 2. БЕЗОПАСНЫЙ РАСЧЕТ И ВСТАВКА QR-КОДА
    verification_url = f"https://onrender.com{data.get('entry_number', '')}"
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    # Чтобы не зависеть от масштаба, берем ширину страницы напрямую
    # Голограмма обычно находится симметрично. Если ширина ~2000, 
    # то отступ справа составит width - 350.
    w = page.rect.width
    # Универсальный квадрат для правого верхнего угла бланка
    qr_rect = fitz.Rect(w - 380, 160, w - 160, 380)
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. ЛЕГКОВЕСНОЕ РАСТРИРОВАНИЕ (Оптимизация под бесплатный Render)
    # dpi=200-250 вполне достаточно, чтобы текст стал невыделяемой картинкой,
    # но сервер не падал по лимитам памяти (OOM)
    pix = page.get_pixmap(dpi=250)
    doc.close()

    image_pdf_bytes = pix.pdf_bytes()
    final_doc = fitz.open("pdf", image_pdf_bytes)
    
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    final_doc.save(output_path, garbage=4, deflate=True)
    final_doc.close()
    
    return output_path
