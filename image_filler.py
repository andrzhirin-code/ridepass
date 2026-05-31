import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")

def fill_order_template(data: dict) -> str:
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    # Список значений в том порядке, в котором поля идут в PDF
    values = [
        data.get("vehicle_type", ""),
        "СИМ",
        data.get("brand", ""),
        data.get("model", ""),
        data.get("year", ""),
        data.get("vin", ""),
        data.get("power", ""),
        data.get("max_speed", ""),
        data.get("full_name", ""),
        data.get("passport", ""),
        data.get("address", ""),
        str(data.get("id", "")),
    ]

    for i, field in enumerate(page.widgets()):
        if i >= len(values):
            break
        if values[i]:
            field.field_value = str(values[i])
            field.update()
            # Удаляем рамку (если нужна)
            field.border_width = 0
            field.fill_color = None

    # Убираем все рамки и фон полей
    for field in page.widgets():
        field.border_width = 0
        field.fill_color = None
        field.update()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
