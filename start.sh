#!/bin/bash
# Запускаем веб-сервер FastAPI в фоне
python3 -m uvicorn web:app --host 0.0.0.0 --port 8000 &
# Запускаем бота
python3 main.py
