import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # Регистрируем шрифт для кириллицы
    try:
        page.insert_font(fontname="ari", fontfile=FONT_PATH)
    except:
        pass

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
            rect = field.rect
            # Затираем виджет, чтобы не мешал
            field.field_value = ""
            field.update()
            # Рисуем текст поверх
            page.insert_textbox(
                rect,
                str(value),
                fontsize=10,
                fontname="ari",
                align=0
            )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, clean=True, deflate=True)
    doc.close()
    return output_path
