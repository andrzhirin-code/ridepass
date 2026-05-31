import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")

def fill_order_template(data: dict) -> str:
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    values = {
        "vehicle_type": data.get("vehicle_type", ""),
        "category": "СИМ",
        "brand": data.get("brand", ""),
        "model": data.get("model", ""),
        "year": data.get("year", ""),
        "vin": data.get("vin", ""),
        "power": data.get("power", ""),
        "max_speed": data.get("max_speed", ""),
        "full_name": data.get("full_name", ""),
        "passport": data.get("passport", ""),
        "address": data.get("address", ""),
        "id": str(data.get("id", "")),
    }

    for field in page.widgets():
        name = field.field_name
        if name in values and values[name]:
            field.field_value = str(values[name])
            field.border_width = 0
            field.fill_color = None
            field.update()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
