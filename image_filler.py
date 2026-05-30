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

    # Регистрируем русский шрифт
    page.insert_font(fontname="ari", fontfile=FONT_PATH)

    for field in page.widgets():
        field_name = field.field_name
        if not field_name:
            continue

        # Ищем значение для этого поля
        value = None
        if field_name in data:
            value = data[field_name]
        elif field_name.lower() == "category":
            value = "СИМ"

        if not value:
            continue

        rect = field.rect
        # Точка для текста (левый край, чуть выше нижней границы)
        point = fitz.Point(rect.x0 + 3, rect.y1 - 4)
        font_size = 11 if field_name != "id" else 14

        # Вставляем текст
        page.insert_text(
            point,
            str(value),
            fontsize=font_size,
            fontname="ari",
            color=(0, 0, 0)
        )

        # Удаляем интерактивное поле (рамку)
        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
