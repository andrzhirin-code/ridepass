import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(TEMPLATE_PATH)
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(FONT_PATH)

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    values = {
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

    text_items = []
    for field in page.widgets():
        name = field.field_name
        if name not in values:
            continue
        rect = field.rect
        text_items.append((
            values[name],
            fitz.Point(rect.x0 + 3, rect.y1 - 4)
        ))
        page.delete_widget(field)

    for text, point in text_items:
        page.insert_text(point, text, fontname="ari", fontsize=11, color=(0.12, 0.16, 0.2))

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_path
