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
    page = doc[0]

    # КРИТИЧЕСКИ ДЛЯ СТИЛЕЙ: Включаем использование оригинальных шрифтов,
    # цветов и размеров, заложенных в самом PDF-шаблоне
    try:
        doc.need_appearances(True)
    except:
        pass

    # Карточка полей
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

    # Заполняем поля формы (автоматически применятся Times New Roman и цвета бланка)
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            field.update()

    # 2. АВТОМАТИЧЕСКИЙ РАСЧЕТ СИММЕТРИИ QR-КОДА
    # Получаем точные размеры текущего бланка
    width = page.rect.width
    height = page.rect.height

    # Голограмма слева занимает диапазон: по X (8.5% - 16.5%), по Y (7.8% - 13.5%)
    # Считаем зеркальные координаты для правой стороны:
    qr_x0 = width * 0.835
    qr_y0 = height * 0.078
    qr_x1 = width * 0.915
    qr_y1 = height * 0.135
    
    qr_rect = fitz.Rect(qr_x0, qr_y0, qr_x1, qr_y1)

    # Генерация QR-кода
    verification_url = f"https://onrender.com{data.get('entry_number', '')}"
    qr = qrcode.QRCode(box_size=10, border=1) # Оптимальный размер сетки для встраивания
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    # Вставляем QR-код строго в рассчитанные симметричные границы
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. ЗАЩИТА ОТ ВЫДЕЛЕНИЯ И КОПИРОВАНИЯ (Растрирование)
    # Отрендерит страницу со всеми примененными оригинальными шрифтами бланка в высоком качестве
    pix = page.get_pixmap(dpi=400)
    doc.close()

    # Сохраняем как монолитное изображение внутри нового PDF
    image_pdf_bytes = pix.pdf_bytes()
    final_doc = fitz.open("pdf", image_pdf_bytes)
    
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    final_doc.save(output_path, garbage=4, deflate=True)
    final_doc.close()
    
    return output_path
