from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas, enums
from fastapi import HTTPException
from app.dependencies import DbDep, paginationParam, PaginationParams
import uuid

from app.OAuth2 import get_password_hash
from .error import add_error , get_error_message
from app import EmailUtil

error_keys = {
    "employeeRole_employee_id_fkey": "No Empolyee with this id",
    "employeeRole_pkey" : "No Employee Role with this id",
    "ck_employees_cnss_number" : "It should be {8 digits}-{2 digits} and it's Mandatory for Cdi and Cdd",
    "employees_email_key" : "Email already used" ,
    "employees_cnss_number_key" : "Cnss number already used",
    "empoyee_ pkey": "No employee with this id" ,
    "errors_employee_id_fkey": "No Empolyee with this id",
}

def get_confirmation_code(db:Session, code: str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

def add_confirmation_code(db: Session , db_employee: models.Employee):
    activation_code = models.AccountActivation(employee_id = db_employee.id, email = db_employee.email, token = uuid.uuid1(), status = enums.TokenStatus.Pending)
    db.add(activation_code)
    return activation_code  


def edit_confirmation_code(db: Session, id : int, new_data : dict):
    db.query(models.AccountActivation).filter(id).update(new_data, synchronize_session=False)
def get(db: Session, id: int):
    #select * from users id = user_id
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def edit_employee(db: Session, id: int , new_data:dict ):
    db.query(models.Employee).filter(models.Employee.id == id ).update(new_data, synchronize_session=False)


def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def div_ceil(nominator, denominator):
    full_pages= nominator // denominator
    additional_page = 1 if nominator % denominator > 0 else 0
    return full_pages + additional_page

def get_employees(db: Session  , pagination_param : PaginationParams, name_substr : str = None ) :
        query = db.query(models.Employee)
        if name_substr : 
            query = query.filter(func.lower(func.concat(models.Employee.firstname,'', models.Employee.lastname)).contains(func.lower(name_substr)))

        total_records = query.count()
        total_pages = div_ceil(total_records, pagination_param.page_size)
        employees = query.limit(pagination_param.page_size).offset((pagination_param.page_number-1)* pagination_param.page_size)
        return (employees, total_records, total_pages)


async def add(db: Session, employee: schemas.EmployeeCreate):
    try :
        employee.password = get_password_hash(employee.password)

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
        add_confirmation_code(db,db_employee)
        #add confirmation code (token)
        
        #db.commit() # idha mayhmkch fil mail teb3ath wala w tzid btn fi lweb bech ynajem mail idha majehouch
        
        activation_code = add_confirmation_code(db, db_employee)

        #send email Confirmation
        await EmailUtil.simple_send([db_employee.email], {
            #'name' : db_employee.firstname,
            'code' : activation_code.token,
            #'psw' : not_hashed_psw
        })

        db.commit()
    except Exception as e : 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500 , detail = get_error_message(text) )
    
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

async def edit_employee(db: Session, id : int , entry  : schemas.EmployeeEdit):
    query = db.query(models.Employee).filter(models.Employee.id == id)
    employee_in_db= query.first()

    if not employee_in_db:
        raise HTTPException(status_code=400, detail = "Employee not found")
    
    fiels_to_update = entry.model_dump()
    for field in ["email", "password", "confirm_passord","roles", "actual_password"]:
        fiels_to_update.pop(field)


    if employee_in_db.email != entry.email:
        if not entry.acutal_Password or get_password_hash(entry.password) != employee_in_db.password:
            raise HTTPException(status_code=400, detail= "Current Password missing or incorrect. It's mandatory to set a new Email" )

        fiels_to_update[models.Employee.email] = entry.email
        fiels_to_update[models.Employee.account_status] = enums.AccountStatus.Inactive

    if entry.password and get_password_hash(entry.password ) != employee_in_db.password:
        if entry.password != entry.confirm_password:
            raise HTTPException(status_code = 400 , detail = "Passwords must match")
        
        if not entry.acutal_Password or get_password_hash(entry.acutal_Password) != employee_in_db.password:
            raise HTTPException(status_code=400, detail= "Current Password missing or incorrect. It's mandatory to set a new password" )
        
        fiels_to_update[models.Employee.password] = get_password_hash(entry.password)
    
    query.update(fiels_to_update, synchronize_session=False)
    db.flush()