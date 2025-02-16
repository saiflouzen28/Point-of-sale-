from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from sqlalchemy import func

from app.crud.employee import get_employees
from app.crud.error import add_error, get_error_message
from ..schemas import EmployeeCreate, EmployeeOut, EmployeeBase, EmployeeGet, BaseOut, ConfirmAccount
from ..database import get_db
from .. import models
from .. import enums
from typing import Annotated
from datetime import datetime
from app.dependencies import DbDep, paginationParam, PaginationParams
from app.services.employee_service import (
    create_employee,
    get_employee,   
    get_employee_by_email,
    get_all_employees,
    update_employee, 
    delete_employee, 
    get_confirmation_code 
)

from app import schemas

router = APIRouter(
    prefix="/employee",
    tags=["Employees"])

@router.post("/", response_model=EmployeeOut)
async def create_employee(employee: EmployeeCreate, db: DbDep):
    if(employee.password != employee.confirm_password):
        raise HTTPException(status_code=400,detail="Passwor most match !")
    
    db_employee = get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    return await create_employee(db, employee=employee)
def div_ceil(nominator, denominator):
    full_pages= nominator // denominator
    additional_page = 1 if nominator % denominator > 0 else 0
    return full_pages + additional_page

@router.get("/all")
def get_all(db: DbDep , pagination_param : paginationParam, name_substr : str = None ) :
    try: 
        employees, total_records, total_pages = get_employees(db,pagination_param, name_substr)
    except Exception as e :
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status = 500 , detail = get_error_message(text))
    return schemas.EmployeesOut(
        status_code=200,
        detail="All employess",
        list=[schemas.EmployeeOut(**employee.__dict__) for employee in employees],
        page_number =pagination_param.page_number,
        page_size = pagination_param.page_size,
        total_pages = total_pages,
        total_records = total_records
    )


""" @router.get("/allEmployees", response_model=List[EmployeeGet])
async def read_employees(
    pagination_param : paginationParam,
    db: DbDep,
):
    return get_all_employees(db, **pagination_param)
 """

@router.get("/{employee_id}", response_model=EmployeeGet)
async def read_employee(employee_id: int, db: DbDep):
    employee = await get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{employee_id}", response_model=EmployeeBase)
async def update_employee_data(employee_id: int, employee: EmployeeCreate,  db: DbDep):
    updated_employee = await update_employee(db, employee_id, employee)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee

@router.delete("/{employee_id}")
async def remove_employee(employee_id: int,  db: DbDep):
    deleted = await delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


