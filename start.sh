#!/bin/bash
python3 -m uvicorn web:app --host 0.0.0.0 --port 8000 &
python3 main.py
