import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "ARIALBD.TTF")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]

    # СООТВЕТСТВИЕ: что в PDF -> ключ из order_data
    # Это нужно подобрать по твоему шаблону (по скриншоту)
    field_mapping = {
        "Text3": "vehicle_type",   # Тип ТС
        "Text4": "category",       # Категория (будет "СИМ")
        "Text5": "brand",          # Марка
        "Text6": "model",          # Модель
        "Text7": "year",           # Год
        "Text8": "vin",            # VIN
        "Text9": "power",          # Мощность
        # если есть другие поля, добавь сюда
        # "Text10": "max_speed",
        # "Text11": "full_name",
        # "Text12": "passport",
        # "Text13": "address",
        # "Text14": "id",
    }

    for field in page.widgets():
        name = field.field_name
        if not name:
            continue
        
        if name in field_mapping:
            key = field_mapping[name]
            if key == "category":
                value = "СИМ"
            else:
                value = data.get(key, "")
            if value:
                field.field_value = str(value)
                field.update()

    page.bake()

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    doc.save(output_path, garbage=4, clean=True, deflate=True)
    doc.close()
    return output_path
