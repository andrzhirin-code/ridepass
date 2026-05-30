import os
from pypdf import PdfReader, PdfWriter

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
        raise FileNotFoundError(f"PDF-шаблон не найден: {TEMPLATE_PATH}")

    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()
    writer.append(reader)

    # Заполняем поля
    writer.update_page_form_field_values(
        writer.pages[0],
        {
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
    )

    # Защита от редактирования (только печать)
    writer.encrypt(
        user_password=None,
        owner_password="ridepass_protect_2026",
        permissions=4  # 4 = только печать, 1 = ничего нельзя
    )

    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    with open(output_path, "wb") as output_file:
        writer.write(output_file, flatten=True)

    return output_path
