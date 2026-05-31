import fitz

doc = fitz.open("template_form.pdf")
page = doc[0]

widgets = sorted(page.widgets(), key=lambda w: (round(w.rect.y0), round(w.rect.x0)))

print("--- СПИСОК ПОЛЕЙ В ВАШЕМ PDF ---")
for i, w in enumerate(widgets, 1):
    print(f"Поле {i}: Имя = '{w.field_name}'")
