from sqlalchemy.orm import Session

from .. import EmailUtil
from .. import models, schemas

async def create_employee(db: Session, employee: schemas.EmployeeBase):
    # fix me later when reading about security in fastapi
    employee.password = employee.password + "notreallyhashed"

    employee_data = employee.model_dump()

    employee_data.pop('confirm_password')
    roles = employee_data.pop('roles')

    #add employee
    db_employee = models.Employee(**employee_data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    #add employee roles
    for role in roles :
        db_role = models.EmployeeRole(role = role, employee_id = db_employee.id)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
    #send email Confiramtion
    await EmailUtil.simple_send([db_employee.email])
    
    return schemas.EmployeeOut(**db_employee.__dict__)

async def get_employee(db: Session, id: int):
    #select * from users id = user_id
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_employee_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_all_employees(db: Session, skip: int = 0, limit : int = 100 ):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def update_employee(db: Session, employee_id: int, employee_update: schemas.EmployeeBase):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        return None
    for key, value in employee_update.dict(exclude_unset=True).items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee

def delete_employee(db: Session, employee_id: int):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        return None
    db.delete(employee)
    db.commit()
    return True

def get_confirmation_code(db: Session, code: str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

