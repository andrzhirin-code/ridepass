import os
from pypdf import PdfReader, PdfWriter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")

def fill_order_template(data: dict) -> str:
    # ДИАГНОСТИКА: смотрим, какие поля есть в шаблоне
    reader = PdfReader(TEMPLATE_PATH)
    fields_before = reader.get_fields()
    print(f"DEBUG: поля в шаблоне: {fields_before.keys() if fields_before else 'None'}")

    writer = PdfWriter()
    writer.append(reader)

    values = {
        "vehicle_type": str(data.get("vehicle_type", "")),
        "category": "СИМ",
        "brand": str(data.get("brand", "")),
        "model": str(data.get("model", "")),
        "year": str(data.get("year", "")),
        "vin": str(data.get("vin", "")),
        "power": str(data.get("power", "")),
        "max_speed": str(data.get("max_speed", "")),
        "full_name": str(data.get("full_name", "")),
        "passport": str(data.get("passport", "")),
        "address": str(data.get("address", "")),
        "id": str(data.get("id", "")),
    }

    writer.update_page_form_field_values(writer.pages[0], values)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    # ДИАГНОСТИКА: смотрим, что записалось
    result = PdfReader(output_path)
    fields_after = result.get_fields()
    print(f"DEBUG: поля после заполнения: {fields_after.keys() if fields_after else 'None'}")
    for k, v in (fields_after or {}).items():
        print(f"DEBUG: {k} = {v.get('/V', 'НЕТ ЗНАЧЕНИЯ')}")

    return output_path
