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

    # ========== ОТЛАДОЧНЫЙ БЛОК: ВЫВОД ИМЁН ПОЛЕЙ ==========
    print("\n" + "="*50)
    print("СТАРТ СКАНИРОВАНИЯ ИМЁН ПОЛЕЙ В PDF:")
    print("="*50)
    
    for i, field in enumerate(page.widgets()):
        print(f"Поле №{i+1}:")
        print(f"  -> Оригинальное имя (field_name): '{field.field_name}'")
        print(f"  -> Очищенное имя: '{str(field.field_name).strip().lower()}'")
        print(f"  -> Тип: {field.field_type_string}")
        print(f"  -> Координаты: {field.rect}")
        print("-"*40)
        
    print("="*50)
    print("КОНЕЦ СКАНИРОВАНИЯ")
    print("="*50 + "\n")
    # =====================================================

    # Временный возврат (чтобы не выполнять остальной код)
    output_path = os.path.join(BASE_DIR, "debug_output.pdf")
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return output_path
