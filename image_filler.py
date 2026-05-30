import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)

    # 1. Заполняем поля
    for page in doc:
        for widget in page.widgets():
            name = widget.field_name
            if not name:
                continue
            if name in data:
                widget.field_value = str(data[name])
                widget.update()
            elif name.lower() == "category":
                widget.field_value = "СИМ"
                widget.update()

    # 2. Перезагружаем каждую страницу
    for i in range(len(doc)):
        doc.reload_page(i)

    # 3. Запекаем форму
    for page in doc:
        try:
            page.bake()
        except:
            pass

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, deflate=True, garbage=4, clean=True)
    doc.close()
    return output_path
