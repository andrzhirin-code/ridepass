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

    field_mapping = {
        "Text3": str(data.get("id", "—")),
        "Text4": str(data.get("id", "—")),
        "Text5": str(data.get("vehicle_type", "—")),
        "Text6": "СИМ",
        "Text7": str(data.get("brand", "—")),
        "Text10": str(data.get("model", "—")),
        "Text12": str(data.get("year", "—")),
        "Text13": str(data.get("vin", "—")),
        "Text16": str(data.get("power", "—")),
        "Text18": str(data.get("max_speed", "—")),
        "Text19": str(data.get("full_name", "—")),
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
                "is_large": (name in ["Text3", "Text4"])
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
