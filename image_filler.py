import os
import urllib.request
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_URL = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
FONT_PATH = os.path.join(BASE_DIR, "Roboto-Regular.ttf")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    # Скачиваем шрифт, если его нет
    if not os.path.exists(FONT_PATH):
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
            print(f"Шрифт загружен: {FONT_PATH}")
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # Регистрируем кириллический шрифт
    if os.path.exists(FONT_PATH):
        page.insert_font(fontname="cyr", fontfile=FONT_PATH)
        fontname = "cyr"
    else:
        fontname = "helv"  # fallback

    for field in page.widgets():
        field_name = field.field_name
        if not field_name:
            continue

        # Получаем значение
        if field_name in data:
            value = data[field_name]
        elif field_name.lower() == "category":
            value = "СИМ"
        else:
            continue

        if not value:
            continue

        rect = field.rect
        point = fitz.Point(rect.x0 + 3, rect.y1 - 4)
        font_size = 14 if field_name == "id" else 11

        page.insert_text(
            point,
            str(value),
            fontsize=font_size,
            fontname=fontname,
            color=(0, 0, 0)
        )

        page.delete_widget(field)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
