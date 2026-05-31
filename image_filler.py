import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    if os.path.exists(FONT_PATH):
        page.insert_font(fontname="ari", fontfile=FONT_PATH)
        fontname = "ari"
    else:
        fontname = "helv"

    # Соответствие: техническое имя поля → ключ из data
    mapping = {
        "Text3":  str(data.get("id", "—")),
        "Text4":  str(data.get("vehicle_type", "—")),
        "Text5":  "СИМ",
        "Text6":  str(data.get("brand", "—")),
        "Text7":  str(data.get("model", "—")),
        "Text10": str(data.get("year", "—")),
        "Text12": str(data.get("vin", "—")),
        "Text13": str(data.get("power", "—")),
        "Text16": str(data.get("max_speed", "—")),
        "Text18": str(data.get("full_name", "—")),
        "Text19": str(data.get("passport", "—")),
        # Если есть поле для address, добавь его сюда (например, Text20)
    }

    # Сначала собираем координаты
    text_items = []
    for field in page.widgets():
        name = field.field_name
        if name in mapping and mapping[name]:
            rect = field.rect
            text_items.append({
                "text": mapping[name],
                "point": fitz.Point(rect.x0 + 4, rect.y1 - 5),
                "is_id": (name == "Text3")
            })

    # Удаляем виджеты (убираем рамки)
    for field in page.widgets():
        page.delete_widget(field)

    # Рисуем текст
    for item in text_items:
        font_size = 14 if item["is_id"] else 11
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=font_size,
            fontname=fontname,
            color=(0.12, 0.16, 0.2)
        )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_path
