import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")

def fill_order_template(data: dict) -> str:
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    # ПОРЯДОК ПОЛЕЙ (сверь с тем, как они идут в PDF)
    field_order = [
        "Text3",   # vehicle_type
        "Text4",   # category
        "Text5",   # brand
        "Text6",   # model
        "Text7",   # year
        "Text8",   # vin
        "Text9",   # power
        "Text10",  # max_speed
        "Text11",  # full_name
        "Text12",  # passport
        "Text13",  # address
        "Text14",  # id
    ]

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

    widgets = list(page.widgets())
    for i, field in enumerate(widgets):
        if i >= len(field_order):
            break
        if values[i]:
            field.field_value = str(values[i])
            field.update()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
