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

    # ЧЁТКАЯ КАРТА КООРДИНАТ (X, Y) — подбери под свой бланк!
    field_coordinates = {
        "id": (1240, 260),
        "vehicle_type": (1080, 583),
        "category": (1080, 630),
        "brand": (1080, 678),
        "model": (1080, 725),
        "year": (1080, 773),
        "vin": (1080, 820),
        "power": (1080, 868),
        "max_speed": (1080, 915),
        "full_name": (1080, 1038),
        "passport": (1080, 1105),
        "address": (1080, 1173),
    }

    # Категория всегда "СИМ"
    if "category" in field_coordinates:
        page.insert_text(
            fitz.Point(field_coordinates["category"][0], field_coordinates["category"][1]),
            "СИМ",
            fontsize=11,
            fontname="ari",
            fontfile=FONT_PATH,
            color=(0.12, 0.16, 0.2)
        )

    # Заполняем остальные поля
    for key, coords in field_coordinates.items():
        if key == "category":
            continue
        value = data.get(key, "")
        if value:
            page.insert_text(
                fitz.Point(coords[0], coords[1]),
                str(value),
                fontsize=11 if key != "id" else 14,
                fontname="ari",
                fontfile=FONT_PATH,
                color=(0.12, 0.16, 0.2)
            )

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
