from typing import Annotated
from fastapi import Depends
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
DbDep = Annotated[Session, Depends(get_db)]

class PaginationParams : 
    def __init__(self, page_size : int = 10 , page_number : int = 1):
        self.page_size  = page_size
        self.page_number = page_number

paginationParam = Annotated[PaginationParams,Depends()]

oaut2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokenDep  = Annotated[str, Depends(oaut2_scheme)]

formDataDep = Annotated[str, Depends(oaut2_scheme)]

def get_current_employee(db:DbDep,token : tokenDep):
    return get_current_employee(db,token)