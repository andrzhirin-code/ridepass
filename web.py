from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from database import get_order_by_entry_number, DB_NAME
import sqlite3
import os

app = FastAPI()

def get_order_by_entry_number(entry_number):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE entry_number = ?", (entry_number,))
    order = cur.fetchone()
    conn.close()
    return order

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RidePass - Проверка документа</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            input { padding: 10px; width: 70%; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .valid { background: #d4edda; border: 1px solid #c3e6cb; }
            .invalid { background: #f8d7da; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <h2>🔍 Проверка подлинности документа RidePass</h2>
        <p>Введите номер документа (например: DP-00073)</p>
        <input type="text" id="code" placeholder="DP-00073">
        <button onclick="check()">Проверить</button>
        <div id="result" class="result"></div>

        <script>
            async function check() {
                const code = document.getElementById('code').value;
                const resultDiv = document.getElementById('result');
                if (!code) {
                    resultDiv.innerHTML = '<div class="invalid">❌ Введите номер документа</div>';
                    return;
                }
                try {
                    const response = await fetch(`/check?code=${code}`);
                    const data = await response.json();
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div class="valid">
                                ✅ <strong>Документ действителен</strong><br><br>
                                📄 Номер: ${data.document.record_number}<br>
                                👤 Владелец: ${data.document.owner}<br>
                                🏍 Марка: ${data.document.brand}<br>
                                🔧 Модель: ${data.document.model}<br>
                                📅 Год: ${data.document.year}<br>
                                🔢 Номер рамы: ${data.document.frame}<br>
                                🔢 Номер двигателя: ${data.document.engine}<br>
                                🔒 Хеш: ${data.document.hash}
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="invalid">❌ ${data.detail}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = '<div class="invalid">❌ Ошибка проверки</div>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/check")
def verify_document(code: str):
    order = get_order_by_entry_number(code)
    if not order:
        raise HTTPException(status_code=404, detail="Документ не найден или поддельный")
    
    return {
        "status": "valid",
        "document": {
            "record_number": order[2],
            "owner": order[22],
            "brand": order[8],
            "model": order[9],
            "year": order[10],
            "frame": order[11],
            "engine": order[12],
            "hash": order[3]
        }
    }
