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

    # 1. Собираем данные о полях
    widgets_data = []
    for field in page.widgets():
        field_name = field.field_name
        if not field_name:
            continue
        
        value = None
        if field_name in data:
            value = data[field_name]
        elif field_name.lower() == "category":
            value = "СИМ"
            
        if value and value != "":
            widgets_data.append({
                "field_name": field_name,
                "rect": field.rect,
                "value": str(value)
            })

    # 2. Сортируем по координатам (сверху вниз, слева направо)
    widgets_data.sort(key=lambda w: (round(w["rect"].y0, 1), w["rect"].x0))

    # 3. Вставляем текст
    for item in widgets_data:
        rect = item["rect"]
        font_size = 11
        page.insert_textbox(
            rect,
            item["value"],
            fontsize=font_size,
            fontname="ari",
            color=(0, 0, 0),
            align=0
        )

    # 4. Удаляем виджеты
    for field in list(page.widgets()):
        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
