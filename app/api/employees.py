# api/employees.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas import EmployeeCreate, EmployeeOut, EmployeeBase, EmployeeGet, BaseOut, ConfirmAccount
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from .. import enums
from typing import Annotated
from datetime import datetime
from app.services.employee_service import (
    create_employee,
    get_employee,   
    get_employee_by_email,
    get_all_employees,
    update_employee, 
    delete_employee, 
    get_confirmation_code 
)

router = APIRouter(
    prefix="/employee",
    tags=["Employees"])

@router.post("/", response_model=EmployeeOut)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):

    if(employee.password != employee.confirm_password):
        raise HTTPException(status_code=400,detail="Passwor most match !")
    
    db_employee = get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    return await create_employee(db, employee=employee)

async def pagination_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@router.get("/allEmployees", response_model=List[EmployeeGet])
async def read_employees(
    pagination: Annotated[dict, Depends(pagination_params)],
    db: Session = Depends(get_db),
):
    return get_all_employees(db, **pagination)


@router.get("/{employee_id}", response_model=EmployeeGet)
async def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = await get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{employee_id}", response_model=EmployeeBase)
async def update_employee_data(employee_id: int, employee: EmployeeCreate,  db: Session = Depends(get_db)):
    updated_employee = await update_employee(db, employee_id, employee)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee

@router.delete("/{employee_id}")
async def remove_employee(employee_id: int,  db: Session = Depends(get_db)):
    deleted = await delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@router.patch("/employee1",response_model=BaseOut)
def confirm_account(confirAccountInput : ConfirmAccount,db: Session =Depends(get_db)):
    confirmation_code = get_confirmation_code(db,confirAccountInput.confirmation_code)

    if not confirmation_code:
        raise HTTPException(status_code= 400, detail="token does not exist")
    
    if confirmation_code.status == enums.TokenStatus.Used: 
        raise HTTPException(status_code = 400, detail = "token already used")
    
    diff = (datetime.now()-confirmation_code.create_on).seconds #seconds

    if diff > 3600 :
        raise HTTPException(status_code=400, detail = "token expired")

    # employee become active => he can start using the app
    db.query(models.Employee).filter(models.Employee.id == confirmation_code.employee_id).\
    update({models.Employee.account_status : enums.AccountStatus.Active}, synchronize_session=False)

    db.commit()
    
    # token used => you cannot use it again 
    db.query(models.AccountActivation).filter(models.AccountActivation.id == confirmation_code.employee_id).\
    update({models.AccountActivation.status : enums.TokenStatus.Used}, synchronize_session=False)

    db.commit()

    return BaseOut(
        detail= "Account confirmed",
        status_code= status.HTTP_200_OK
    )
