import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
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

    widgets = list(page.widgets() or [])

    for field in widgets:
        name = field.field_name
        if name not in values:
            continue

        rect = field.rect

        # Закрашиваем поле белым (убираем старый текст)
        page.draw_rect(rect, color=None, fill=(1, 1, 1))

        # Вставляем новый текст
        page.insert_textbox(
            rect,
            values[name],
            fontsize=11,
            fontname="ari",
            color=(0, 0, 0),
            align=0
        )

        # Удаляем виджет
        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path
