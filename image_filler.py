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
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    for field in page.widgets():
        field_name = field.field_name
        if not field_name:
            continue
        
        value = data.get(field_name)
        if not value:
            continue
        
        rect = field.rect
        point = fitz.Point(rect.x0 + 3, rect.y1 - 5)
        page.insert_text(point, str(value), fontsize=11, fontname="ari", color=(0, 0, 0))
        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
