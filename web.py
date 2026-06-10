from fastapi import FastAPI, HTTPException
from database import get_order_by_entry_number
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "RidePass Document Verification Service"}

@app.get("/check")
def verify_document(code: str):
    order = get_order_by_entry_number(code)
    if not order:
        raise HTTPException(status_code=404, detail="Document not found or invalid")
    
    return {
        "status": "valid",
        "document": {
            "record_number": order[2], # unique_doc_number
            "owner": order[16],        # full_name
            "brand": order[5],         # brand
            "model": order[6],         # model
            "year": order[7],          # year
            "frame": order[8],         # frame_number
            "engine": order[9],        # engine_number
            "hash": order[3]           # doc_hash
        }
    }
