from sqlalchemy.orm import Session
from .. import models, schemas

def get(db: Session, id:int):
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_by_email(db: Session, email:str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_all(db:Session , skip : int =0  , limit : int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def add(db: Session, employee : schemas.EmploueeCreate):
    fake_hashed_password = employee.password + "notreallyhashed"
    db_employee = models.Employee(**employee.model_dump(), hashed_password = fake_hashed_password)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return employee