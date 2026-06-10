import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF") # Нужен для резервного копирования, если шрифт не вшит

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # 1. Открываем исходный документ
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # ГРАМОТНОЕ РЕШЕНИЕ ДЛЯ ШРИФТОВ И ЦВЕТА:
    # Говорим PDF-программе использовать встроенные стили оформления самих полей бланка
    try:
        doc.need_appearances(True)
    except:
        pass

    # Карта заполнения полей
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

    # Заполняем поля формы, сохраняя оригинальный стиль каждой ячейки
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            field.update()

    # 2. ГЕНЕРАЦИЯ СИММЕТРИЧНОГО QR-КОДА
    verification_url = f"https://onrender.com{data.get('entry_number', '')}"
    
    # Задаем минимальный внутренний отступ (border=1), чтобы QR-код визуально был крупнее и четче
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    # ИСПРАВЛЕНИЕ: Симметричные координаты относительно левой голограммы.
    # Размер 200x200 пикселей, Y-высота полностью совпадает с голограммой (200-400)
    qr_rect = fitz.Rect(1350, 200, 1550, 400)
    page.insert_image(qr_rect, stream=qr_bytes)

    # 3. ПРОФЕССИОНАЛЬНОЕ РАСТРИРОВАНИЕ ДЛЯ ЗАЩИТЫ ОТ КОПИРОВАНИЯ
    # Повышаем DPI до 400. Текст визуально станет неотличим от векторного, 
    # границы букв Times New Roman будут идеально четкими, но выделить их будет нельзя.
    pix = page.get_pixmap(dpi=400)
    doc.close()

    # Создаем финальный "чистый" PDF из получившейся картинки высокого разрешения
    image_pdf_bytes = pix.pdf_bytes()
    final_doc = fitz.open("pdf", image_pdf_bytes)
    
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    
    # Сохраняем со сжатием, чтобы компенсировать высокий DPI
    final_doc.save(output_path, garbage=4, deflate=True)
    final_doc.close()
    
    return output_path
