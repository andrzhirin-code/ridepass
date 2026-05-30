import os
import fitz
import pikepdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def normalize_pdf(input_path, output_path):
    """Пересохраняем PDF через pikepdf (убирает XFA, восстанавливает структуру)"""
    with pikepdf.open(input_path) as pdf:
        pdf.save(output_path, recompress_flate=True)

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # Нормализуем PDF
    fixed_path = os.path.join(BASE_DIR, "fixed_template.pdf")
    normalize_pdf(TEMPLATE_PATH, fixed_path)

    doc = fitz.open(fixed_path)
    page = doc[0]

    for field in page.widgets():
        name = field.field_name
        if not name:
            continue
        
        if name in data:
            value = data[name]
        elif name.lower() == "category":
            value = "СИМ"
        else:
            continue
        
        if value:
            field.field_value = str(value)
            field.update()

    page.bake()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, clean=True, deflate=True)
    doc.close()

    # Удаляем временный файл
    if os.path.exists(fixed_path):
        os.remove(fixed_path)

    return output_path
