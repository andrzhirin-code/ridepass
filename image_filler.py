import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # ИСПРАВЛЕННАЯ КАРТА ПОЛЕЙ (смещение устранено)
    field_mapping = {
        "Text3": str(data.get("vehicle_type", "—")),  # 1. Тип ТС
        "Text4": "СИМ",                               # 2. Категория
        "Text5": str(data.get("brand", "—")),         # 3. Марка
        "Text6": str(data.get("model", "—")),         # 4. Модель
        "Text7": str(data.get("year", "—")),          # 5. Год выпуска
        "Text10": str(data.get("vin", "—")),          # 6. Идентификационный номер
        "Text12": str(data.get("power", "—")),        # 7. Мощность двигателя
        "Text13": str(data.get("max_speed", "—")),    # 8. Максимальная скорость
        "Text16": str(data.get("full_name", "—")),    # 1. ФИО
        "Text18": str(data.get("passport", "—")),     # 2. Паспорт
        "Text19": str(data.get("address", "—")),      # 3. Адрес
    }

    text_queue = []
    widgets = list(page.widgets())

    for field in widgets:
        name = field.field_name
        if name in field_mapping:
            rect = field.rect
            text_queue.append({
                "text": field_mapping[name],
                "point": fitz.Point(rect.x0 + 4, rect.y1 - 5),
                "is_large": False  # убираем увеличенный шрифт
            })

    for field in widgets:
        page.delete_widget(field)

    page.insert_font(fontname="ari", fontfile=FONT_PATH)
    for item in text_queue:
        font_size = 14 if item["is_large"] else 11
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=font_size,
            fontname="ari",
            color=(0.12, 0.16, 0.2)
        )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
