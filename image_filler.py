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

    form_data = {
        "vehicle_type": str(vehicle_type) if vehicle_type else "Не указано",
        "category": "СИМ",
        "brand": str(brand) if brand else "Не указано",
        "model": str(model) if model else "Не указано",
        "year": str(year) if year else "Не указано",
        "vin": str(vin) if vin else "Не указано",
        "power": str(power) if power else "Не указано",
        "max_speed": str(max_speed) if max_speed else "Не указано",
        "full_name": str(full_name) if full_name else "Не указано",
        "passport": str(passport) if passport else "Не указано",
        "address": str(address) if address else "Не указано",
    }

    for field in page.widgets():
        field_name = field.field_name
        if field_name in form_data:
            field.field_value = form_data[field_name]
            field.field_flags |= fitz.PDF_FIELD_IS_READ_ONLY
            field.update()

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    doc.save(output_path, incremental=False, flatten=True)
    doc.close()

    return output_path
