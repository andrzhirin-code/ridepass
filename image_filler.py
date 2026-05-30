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

    # ОТЛАДКА: выводим реальные имена полей
    print("=== РЕАЛЬНЫЕ ИМЕНА ПОЛЕЙ В PDF ===")
    for field in page.widgets():
        print(f"Имя поля: '{field.field_name}'")
    print("==================================")

    # Заполняем поля и убираем фон/границы
    for field in page.widgets():
        pdf_field_name = field.field_name.strip().lower() if field.field_name else ""
        for key, value in form_data.items():
            if key.lower() in pdf_field_name:
                field.field_value = value
                field.fill_color = None      # убираем серый фон
                field.border_color = None    # убираем рамку
                field.border_width = 0
                field.update()
                print(f"Заполнено поле '{field.field_name}' значением '{value}'")
                break

    # Сплющивание
    pdf_bytes = doc.convert_to_pdf()
    doc.close()

    flattened_doc = fitz.open("pdf", pdf_bytes)
    output_path = os.path.join(BASE_DIR, f"order_{order_id}.pdf")
    flattened_doc.save(output_path, garbage=3, deflate=True)
    flattened_doc.close()

    return output_path
