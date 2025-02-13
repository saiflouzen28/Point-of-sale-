from sqlalchemy.orm import Session
from . import models, schemas, EmailUtil,enums
from fastapi import HTTPException
import uuid


def get(db: Session, id: int):
    #select * from users id = user_id
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

error_keys = {
    "employeeRole_employee_id_fkey": "No Empolyee with this id",
    "employeeRole_pkey" : "No Employee Role with this id",
    "ck_employees_cnss_number" : "It should be {8 digits}-{2 digits} and it's Mandatory for Cdi and Cdd",
    "employees_email_key" : "Email already used" ,
    "employees_cnss_number_key" : "Cnss number already used",
    "empoyee_ pkey": "No employee with this id" ,
    "errors_employee_id_fkey": "No Empolyee with this id",
}

def get_error_message(error_message):
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


async def add(db: Session, employee: schemas.EmployeeBase):
    try :
        # fix me later when reading about security in fastapi
        not_hashed_psw = employee.password 
        employee.password = employee.password + "notreallyhashed"

        employee_data = employee.model_dump()

        employee_data.pop('confirm_password')
        roles = employee_data.pop('roles')

        #add employee
        db_employee = models.Employee(**employee_data)
        db.add(db_employee)
        db.flush()
        # != add session.rollback() session aly hya db
        #add employee roles
        #for role in roles :
        #   db_role = models.EmployeeRole(role = role, employee_id = db_employee.id)
        #   db.add(db_role)
        #   db.commit()
        #   db.refresh(db_role)

        db.add_all([models.EmployeeRole(role = role, employee_id = db_employee.id) for role in roles])

        #add confirmation code (token)
        activation_code = models.AccountActivation(employee_id = db_employee.id, email = db_employee.email, token = uuid.uuid1(), status = enums.TokenStatus.Pending)
        db.add(activation_code)
        db.commit() # idha mayhmkch fil mail teb3ath wala w tzid btn fi lweb bech ynajem mail idha majehouch


        #send email Confirmation
        await EmailUtil.simple_send([db_employee.email], {
            #'name' : db_employee.firstname,
            'code' : activation_code.token,
            #'psw' : not_hashed_psw
        })

        #db.commit()
    except Exception as e : 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500 , detail = get_error_message(str(e)) )
    
    return schemas.EmployeeGet(**db_employee.__dict__)


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.EmployeeCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_confirmation_code(db: Session, code: str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

