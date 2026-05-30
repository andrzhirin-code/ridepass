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

    form_data = {
        "id": str(data.get("id", "—")),
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
        "address": str(data.get("address", "—")),
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
        font_size = 14 if item.get("is_id") else 11
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=font_size,
            fontname="ari",
            color=(0.12, 0.16, 0.2)
        )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
