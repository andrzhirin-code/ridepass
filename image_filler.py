import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(
    order_id: str,
    vehicle_type: str,
    brand: str,
    model: str,
    year: str,
    vin: str,
    power: str,
    max_speed: str,
    full_name: str,
    passport: str,
    address: str
) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # Данные из бота
    form_data = {
        "vehicle_type": str(vehicle_type) if vehicle_type else "",
        "category": "СИМ",
        "brand": str(brand) if brand else "",
        "model": str(model) if model else "",
        "year": str(year) if year else "",
        "vin": str(vin) if vin else "",
        "power": str(power) if power else "",
        "max_speed": str(max_speed) if max_speed else "",
        "full_name": str(full_name) if full_name else "",
        "passport": str(passport) if passport else "",
        "address": str(address) if address else "",
    }

    # Заполняем поля
    for field in page.widgets():
        field_name = field.field_name.strip().lower() if field.field_name else ""
        for key, value in form_data.items():
            if key.lower() in field_name:
                field.field_value = value
                field.update()
                break

    # ГЛАВНОЕ: удаляем все рамки и фоны полей
    page.bake_form_fields()

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()

    return output_path
