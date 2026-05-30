import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    mapping = {
        "Text3": "vehicle_type",
        "Text4": "category",
        "Text5": "brand",
        "Text6": "model",
        "Text7": "year",
        "Text8": "vin",
        "Text9": "power",
    }

    for field in page.widgets():
        name = field.field_name
        if not name:
            continue
        if name in mapping:
            key = mapping[name]
            if key == "category":
                value = "СИМ"
            else:
                value = data.get(key, "")
            if value:
                field.field_value = str(value)
                field.update()

    # Убираем bake/flatten — просто сохраняем
    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path
