

from fastapi import HTTPException
from app import models


def get_error_message(error_message ,error_keys):
    for error_key in error_keys:
        if error_key in error_message: 
            return error_keys[error_key]
    return "Somthing went wrong"

def add_error(text, employee_id, db):
    try: 
        db.add(models.Error(
            text= text,
        ))
        db.commit()
    except Exception as e :
        raise HTTPException(status_code=500 , detail =  "Somthing went wrong")
