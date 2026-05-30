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

    # Тестовые значения, если данные пустые
    form_data = {
        "id": str(data.get("id", "1")),
        "vehicle_type": str(data.get("vehicle_type", "Электросамокат")),
        "category": "СИМ",
        "brand": str(data.get("brand", "Тест Марка")),
        "model": str(data.get("model", "Тест Модель")),
        "year": str(data.get("year", "2026")),
        "vin": str(data.get("vin", "TEST-VIN-12345")),
        "power": str(data.get("power", "3000W")),
        "max_speed": str(data.get("max_speed", "55 км/ч")),
        "full_name": str(data.get("full_name", "Иванов Иван Иванович")),
        "passport": str(data.get("passport", "4512 123456")),
        "address": str(data.get("address", "г. Москва, ул. Ленина, д. 1")),
    }

    text_queue = []

    for field in page.widgets():
        field_name = str(field.field_name).strip().lower()
        if field_name in form_data:
            rect = field.rect
            text_queue.append({
                "text": form_data[field_name],
                "point": fitz.Point(rect.x0 + 4, rect.y1 - 5),
                "is_id": (field_name == "id")
            })

    for field in page.widgets():
        page.delete_widget(field)

    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    for item in text_queue:
        font_size = 14 if item["is_id"] else 11
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
