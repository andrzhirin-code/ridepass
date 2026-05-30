import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]  # работаем с первой страницей

    # Вставляем шрифт для кириллицы
    try:
        page.insert_font(fontname="ari", fontfile=FONT_PATH)
    except:
        pass

    # Заполняем поля
    for field in page.widgets():
        name = field.field_name
        if not name:
            continue
        
        # Получаем значение
        if name in data:
            value = data[name]
        elif name.lower() == "category":
            value = "СИМ"
        else:
            continue
        
        if value:
            # Ставим значение в поле
            field.field_value = str(value)
            # Принудительно обновляем
            field.update()
            # Пытаемся задать шрифт
            try:
                field.text_font = "ari"
            except:
                pass

    # Сохраняем с флагом, который убирает интерактивность
    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
