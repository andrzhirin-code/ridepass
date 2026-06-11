import os
import fitz
import qrcode
import gc
import asyncio
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def _sync_fill_order_template(data: dict) -> str:
    print(f"📝 fill_order_template: старт безопасной генерации")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    entry_num = data.get('entry_number', 'temp')
    temp_filled_path = os.path.join(BASE_DIR, f"temp_filled_{entry_num}.pdf")
    final_output_path = os.path.join(BASE_DIR, f"order_{entry_num}.pdf")

    # СТЕП 1: Открываем исходный шаблон формы
    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    field_mapping = {
        "record_number": str(data.get('passport_number', '')).replace("№", ""),
        "series": data.get('series_code', ''),
        "entry_number": str(entry_num),
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

    top_y0, top_y1 = None, None

    # СТЕП 2: Решение проблемы сброса шрифтов по рецептам GitHub PyMuPDF
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            field.field_value = field_mapping[name]
            
            try:
                field.text_font = "TiRo"
            except Exception:
                pass
            
            field.update()
            
            if name in ("record_number", "series"):
                top_y0 = field.rect.y0
                top_y1 = field.rect.y1

    # Быстрое сохранение на диск БЕЗ тяжелого кэширования
    doc.save(temp_filled_path, deflate=True)
    doc.close()

    # СТЕП 3: Открываем файл заново
    render_doc = fitz.open(temp_filled_path)
    render_page = render_doc.load_page(0)
    rect = render_page.rect
    
    # СТЕП 4: Безопасное нанесение QR-кода
    w = float(rect.x1)
    y0 = top_y0 if top_y0 is not None else rect.y1 * 0.078
    y1 = top_y1 if top_y1 is not None else rect.y1 * 0.135
    qr_size = y1 - y0

    qr_rect = fitz.Rect(w - qr_size - (w * 0.05), y0, w - (w * 0.05), y1)
    verification_url = f"https://ridepass.onrender.com/check?code={entry_num}"
    
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    render_page.insert_image(qr_rect, stream=qr_bytes)

    # Делаем легковесный снимок страницы (DPI=120)
    pix = render_page.get_pixmap(dpi=120, alpha=False)
    render_doc.close()

    # СТЕП 5: Создаем финальный растровый документ
    dst_doc = fitz.open()
    new_page = dst_doc.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(rect, pixmap=pix)
    
    pix = None

    # Финальное сохранение с глубокой очисткой структуры
    dst_doc.save(final_output_path, garbage=3, deflate=True, clean=True)
    dst_doc.close()

    # СТЕП 6: Удаляем временный промежуточный файл
    if os.path.exists(temp_filled_path):
        os.remove(temp_filled_path)

    # Принудительное освобождение RAM для бесплатного тарифа Render
    fitz.TOOLS.store_shrink(100)
    gc.collect()
    
    print(f"✅ Документ успешно защищен и сохранен: {final_output_path}")
    return final_output_path

async def fill_order_template(data: dict) -> str:
    return await asyncio.to_thread(_sync_fill_order_template, data)
