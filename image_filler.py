import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    form_data = {
        "vehicle_type": str(data.get("vehicle_type", "—")),
        "category": "СИМ",
        "brand": str(data.get("brand", "—")),
        "model": str(data.get("model", "—")),
        "year": str(data.get("year", "—")),
        "vin": str(data.get("vin", "—")),
        "power": str(data.get("power", "—")),
        "max_speed": str(data.get("max_speed", "—")),
        "full_name": str(data.get("full_name", "—")),
        "passport": str(data.get("passport", "—")),
        "address": str(data.get("address", "—"))
    }

    text_queue = []

    # 1. Сканируем поля и запоминаем их координаты
    for field in page.widgets():
        pdf_field_name = str(field.field_name).strip().lower()
        
        for key, value in form_data.items():
            if key in pdf_field_name or (key == "address" and "addres" in pdf_field_name):
                rect = field.rect
                pos_x = rect.x0 + 2
                pos_y = rect.y1 - 4
                text_queue.append({
                    "text": value,
                    "point": fitz.Point(pos_x, pos_y),
                    "is_id": (key == "id")
                })
                break

    # 2. Удаляем все серые и белые обводки (виджеты)
    for field in page.widgets():
        page.delete_widget(field)

    # 3. Наносим чистый печатный текст
    for item in text_queue:
        font_size = 14 if item.get("is_id") else 11
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=font_size,
            fontname="hebo",
            color=(0.1, 0.14, 0.17)
        )

    order_id = data.get("id", "temp")
    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()

    return output_path
