import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # Диагностика: пишем в логи Render
    widgets = list(page.widgets())
    print(f"DEBUG widgets count: {len(widgets)}")
    for w in widgets:
        print(f"DEBUG field: {w.field_name}")

    output_path = os.path.join(BASE_DIR, "debug.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
