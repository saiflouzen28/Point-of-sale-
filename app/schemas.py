from datetime import date
from pydantic import BaseModel, EmailStr ,Field
from app.enums import Gender, ContractType, AccountStatus, RoleType
from datetime import datetime
from typing import List, Optional

from app.enums.matchyComparer import Comparer
from app.enums.matchyConditionProperty import ConditionProperty
from app.enums.matchyFieldType import FieldType

class OurBaseModle(BaseModel):
    class Config:
        from_attributes = True

class BaseOut(OurBaseModle):
    detail : str 
    status_code : int   

class PagedResponse(BaseOut):
    page_number : int 
    page_size : int 
    total_pages: int 
    total_records: int 

class EmployeeBase(OurBaseModle):
    firstname : str
    lastname : str
    email : str
    number : int 
    birth_date : date | None = None
    address : str | None = None
    gender :  Gender
    roles : List[RoleType]
    phone_number : int 
    contract_type : ContractType
    cnss_number : str | None = None

    
class EmployeeGet(OurBaseModle):
    firstname : str
    lastname : str
    email : str
    number : int 
    birth_date : date | None = None
    address : str | None = None
    gender :  Gender
    phone_number : int 
    contract_type : ContractType
    cnss_number : str | None = None

class EmployeeCreate(EmployeeBase):
    password : str | None = None
    confirm_password : str | None = None 

class EmployeeEdit(EmployeeCreate):
    acutal_Password: str | None = None 
class EmployeeOut(EmployeeBase):
    id : int 
    created_on : datetime

class EmployeesOut(PagedResponse):
    list: List[EmployeeOut]

class ConfirmAccount(OurBaseModle):
    confirmation_code : str 

class ForgetPassword(OurBaseModle):
    email: EmailStr
class Token(BaseModel):
    access_token: str
    token_type: str
    
class MatchyCondition(OurBaseModle):
    property : ConditionProperty
    comparer : Optional[Comparer]
    value : int | float | str | List[str]
    custom_fail_message : Optional[str] = None

class MatchyOption(OurBaseModle):
    display_value : str 
    value : Optional[str] = None
    mandatory: Optional[bool] = False
    type : FieldType
    conditions : Optional[List[MatchyCondition]] = []

class ImportPossibleFields(OurBaseModle):
    possible_fields : List[MatchyOption] = []

class MatchyCell(BaseModel):
    value : str 
    rowIndex : int 
    colIndex : int 

class MatchyUploadEntry(BaseModel):
    lines : List[dict[str,MatchyCell]]
    forceUpload : Optional[bool] =False 

class MatchyWrongCell(OurBaseModle):
    messeage : str
    rowIndex : int 
    colIndex : int 

class ImportResponse(OurBaseModle):
    errors : str 
    warnings : str
    wrongCells : list[MatchyWrongCell]
