import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    for field in page.widgets():
        field_name = field.field_name
        if not field_name:
            continue
        
        value = None
        if field_name in data:
            value = data[field_name]
        elif field_name.lower() == "category":
            value = "СИМ"
        
        if value:
            field.field_value = str(value)
            field.update()

    # Запекаем форму (убираем рамки и делаем текст обычным)
    doc.bake()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
