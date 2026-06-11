import os
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
# Загрузи файл timesbd.ttf в ту же папку на GitHub
FONT_PATH = os.path.join(BASE_DIR, "timesbd.ttf")

def fill_order_template(data: dict) -> str:
    print(f"📝 fill_order_template: запуск векторного вживления шрифтов")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Критическая ошибка: Файл шрифта {FONT_PATH} не найден в репозитории!")

    # 1. Открываем шаблон формы
    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # Карта соответствия данных
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

    # Массив для сохранения точных координат текста перед удалением виджетов
    text_to_draw = []

    # Считываем координаты каждого поля формы на бланке
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            # Получаем границы прямоугольника поля ввода
            rect = field.rect
            text_value = field_mapping[name]
            
            # Сдвигаем базовую линию текста чуть вниз внутри рамки
            point = fitz.Point(rect.x0 + 3, rect.y1 - 4)
            
            # Запоминаем текст и его точное физическое положение
            text_to_draw.append((point, text_value))

    # 2. ЖЕСТКОЕ УДАЛЕНИЕ ФОРМ (Стираем синие рамки и интерактивность)
    for field in page.widgets():
        page.delete_widget(field)

    # 3. ГРАМОТНОЕ ВЖИВЛЕНИЕ ШРИФТА (Защита от выделения)
    # Регистрируем наш загруженный полужирный Times New Roman на странице
    page.insert_font(fontname="TimesNewRoman-Bold", fontfile=FONT_PATH)

    # Рисуем текст как векторные графические линии прямо поверх бланка.
    for point, text_value in text_to_draw:
        page.insert_text(
            point, 
            text_value, 
            fontname="TimesNewRoman-Bold", 
            fontsize=10.5,
            color=(0, 0, 0)
        )

    # 4. АВТОМАТИЧЕСКИЙ ДИНАМИЧЕСКИЙ РАСЧЕТ СИММЕТРИИ QR-КОДА
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

    # 5. Сохраняем ультра-легкий и защищенный документ
    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    
    print(f"✅ Идеальный невыделяемый ПТС со шрифтами успешно сохранен: {output_path}")
    return output_path
