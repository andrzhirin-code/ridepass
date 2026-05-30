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

    # Двухуровневая сортировка: сначала по строке (Y), затем по X
    widgets = [w for w in page.widgets()]
    widgets.sort(key=lambda w: (round(w.rect.y0 / 10) * 10, w.rect.x0))

    # Порядок значений должен строго соответствовать порядку полей на бланке
    ordered_values = [
        "",                                   # Серия RP (не заполняем)
        "",                                   # ID (не заполняем)
        str(data.get("id", "—")),             # № записи
        str(data.get("vehicle_type", "—")),   # Тип ТС
        "СИМ",                                # Категория
        str(data.get("brand", "—")),          # Марка
        str(data.get("model", "—")),          # Модель
        str(data.get("year", "—")),           # Год
        str(data.get("vin", "—")),            # VIN
        str(data.get("power", "—")),          # Мощность
        str(data.get("max_speed", "—")),      # Скорость
        str(data.get("full_name", "—")),      # ФИО
        str(data.get("passport", "—")),       # Паспорт
        str(data.get("address", "—")),        # Адрес
    ]

    text_queue = []
    for i, field in enumerate(widgets):
        if i >= len(ordered_values):
            break
        if i in [0, 1] or not ordered_values[i]:
            continue

        rect = field.rect
        text_queue.append({
            "text": ordered_values[i],
            "point": fitz.Point(rect.x0 + 4, rect.y1 - 5),
            "is_id": (i == 2)
        })

    # Удаляем виджеты (убираем рамки и фоны)
    for field in widgets:
        page.delete_widget(field)

    # Вставляем текст с использованием шрифта
    for item in text_queue:
        font_size = 14 if item["is_id"] else 11
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=font_size,
            fontname="ari",
            fontfile=FONT_PATH,
            color=(0.12, 0.16, 0.2)
        )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()

    return output_path
