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
            "record_number": order[2],      # unique_doc_number
            "owner": order[22],             # full_name
            "brand": order[9],              # brand
            "model": order[10],             # model
            "year": order[11],              # year
            "frame": order[12],             # frame_number
            "engine": order[13],            # engine_number
            "hash": order[3]                # doc_hash
        }
    }
