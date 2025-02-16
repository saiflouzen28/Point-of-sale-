from datetime import datetime , timedelta , timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models, enums
from app import EmailUtil
from app.dependencies import DbDep
from .database import SessionLocal, engine
from .schemas import EmployeeBase, EmployeeCreate, EmployeeOut, EmployeeGet, Token
from .routers import employees
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
import re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Replace with the Angular app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "saif@example.com",
        "full_name": "John Doe",
        "email": "saif@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
@app.get("/employee1/allEmployees")
async def get_employees():
    return [{"id": 1, "name": "John Doe", "position": "Manager"}]

# Dependency




@app.post("/employee12/", response_model=EmployeeGet)
async def create_user(employee: EmployeeCreate, db: DbDep):
    if(employee.password != employee.confirm_password):
        raise HTTPException(status_code=400,detail="Password most match !")

    return await crud.add(db=db, employee=employee)

@app.get("/email")
async def root():
    return await EmailUtil.simple_send(["s@gmail.com"],{
        "first_name" : "saif",
        "last_name": "louzen"
    })

@app.patch("/employee1",response_model=schemas.BaseOut)
def confirm_account(confirAccountInput : schemas.ConfirmAccount,db: DbDep):
    confirmation_code = crud.get_confirmation_code(db,confirAccountInput.confirmation_code)

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

    return schemas.BaseOut(
        detail= "Account confirmed",
        status_code= status.HTTP_200_OK
    )

# Include the employees router to make all employee-related endpoints available
app.include_router(employees.router)

email_regex = r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
cnss_number_regex = r"^\d{8}-\d{2}$"
phone_number_regex =r"^\+216\d{8}$"

mandatory_fields = {
    "first_name" : "First Name",
    "last_name" : "Last Name",
    "email" : "Email",
    "password": "Password",
    "number" : "Number" , 
    "contract_type" : "Contract Type",
    "gender" : "Gender" , 
    "employee_roles" :"Roles",
}

optional_fields = {
    "birth_date" : "Birth Date",
    "address" : "Address",
    "phone_number" : "Phone Number"
} 

mandatory_with_condition ={
    "cnss_number" :("Cnss Number" , lambda employee : isCdiOrCdd(employee))
}

possible_fields = {
    **mandatory_fields,
    **optional_fields,
    **mandatory_with_condition
}

unique_fields ={
    "email" : models.Employee.email,
    "number" : models.Employee.number
}  
options = [
    schemas.MatchyOption(
        display_value=mandatory_fields["first_name"],
        value="first_name",
        mandatory=True,
        type=enums.FieldType.string
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["last_name"],
        value="last_name",
        mandatory=True,
        type=enums.FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["email"],
        value="email",
        mandatory=True,
        type=enums.FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=enums.ConditionProperty.regex,
                comparer=enums.Comparer.e,
                value=email_regex,
            ),
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["password"],
        value="password",
        mandatory=True,
        type=enums.FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["number"],
        value="number",
        mandatory=True,
        type=enums.FieldType.integer,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["birth_date"],
        value="birth_date",
        mandatory=False,
        type=enums.FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["address"],
        value="address",
        mandatory=False,
        type=enums.FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_with_condition["cnss_number"][0],
        value="cnss_number",
        mandatory=False,
        type=enums.FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=enums.ConditionProperty.value,
                comparer=enums.Comparer._in,
                value=enums.ContractType.getPossibleValues(),
            ),
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["contract_type"],
        value="contract_type",
        mandatory=True,
        type=enums.FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=enums.ConditionProperty.value,
                comparer=enums.Comparer._in,
                value=enums.ContractType.getPossibleValues(),
            ),
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["gender"],
        value="gender",
        mandatory=True,
        type=enums.FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=enums.ConditionProperty.value,
                comparer=enums.Comparer._in,
                value=enums.Gender.getPossibleValues(),
            ),
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["employee_roles"],
        value="employee_roles",
        mandatory=True,
        type=enums.FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["phone_number"],
        value="phone_number",
        mandatory=False,
        type=enums.FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=enums.ConditionProperty.regex,
                comparer=enums.Comparer.e,
                value=phone_number_regex,
            ),
        ],
    ),
]

def is_regex_matched(pattern, field):
    return field if re.match(pattern, field) else None

def is_valid_email(field):
    return field if is_regex_matched(email_regex,field) else None

def is_positive_int(x):
    try:
        x = int(x)  
        if x >= 0:  
            return True
    except (ValueError, TypeError):
        return None
    return None

def is_valid_date(date):
    try:
        obj = datetime.strptime(date, '%d%m%Y')
        return obj.isoformat
    except:
        return None

def isCdiOrCdd(employee):
    return employee["contract_type"].value in [enums.ContractType.Cdi, enums.ContractType.Cdd]

def is_valid_cnss_number(employee, field):
    return field if is_regex_matched(cnss_number_regex,field) else None

def is_valid_phone_number(field):
    return field if is_regex_matched(phone_number_regex,field) else None

def are_roles_valid(field):
    res = []
    for role_name in field.split(','):
        val = enums.RoleType.is_valid_enum_value(role_name)
        if not val:
            return None
        res.append(val)
    return res #[enums.RoleType.Admin, enums.RoleType.Vendor]
fields_check = {
    "email" : (lambda employee : is_valid_email(employee["email"]),"wrong Email format"),
    "gender" : (lambda employee : enums.Gender.is_valid_enum_value(employee["gender"]),f"Possible valuse are : {enums.Gender.getPossibleValues()}"),
    "contract_type" : (lambda employee : enums.ContractType.is_valid_enum_value(employee["contract_type"]),f"Possible valuse are:{enums.ContractType.getPossibleValues()}"),
    "number" : (lambda employee : is_positive_int(employee["number"]),"It should be an integer >=0"),
    "birth_date" : (lambda employee : is_valid_date(employee["birth_date"]),"Date format should be dd/mm/yyyy"),
    "cnss_number" : (lambda employee, field : is_valid_cnss_number(field),"It should be {8 digits}={2 digits} and it's Mandatory for Cdi and Cdd"),
    "phone_number" : (lambda employee, field : is_valid_phone_number(field),"Phone number is not valid for Tunisia, it shoud be of 2 Digits"),
    "emplyee_roles" : (lambda employee, field : is_valid_email(field),f"Possible valuse are:{enums.ContractType.getPossibleValues()}")
}
def is_field_mandatory(employee, field):
    return field in mandatory_fields or (field in mandatory_with_condition and mandatory_with_condition[field][1](employee))

#employee wehed
def validate_employee_data(employee):
    errors =[]
    warnings = []
    wrong_cells =[]
    employee_to_add = {field : cell.value for field , cell in employee.items()}
    for field in possible_fields:
        if field not in employee:
            if is_field_mandatory(employee, field):
                errors.append(f"{possible_fields[field]} is mandatory but missing")
        cell = employee[field]
        employee_to_add[field] = employee_to_add[field].strip()

        if employee_to_add[field] =='':
            if is_field_mandatory():
                msg = f'{possible_fields[field]} is mandatory but missing'
                errors.append(msg)
                wrong_cells.append(schemas.MatchWrongCell(msg, cell.rowIndex , cell.colIndex))
            else : 
                employee_to_add[field] = None
        elif field in fields_check : 
            converted_val = fields_check[field][0](employee_to_add[field])
            if converted_val is None :
                message = fields_check[field][1]
                (errors if is_field_mandatory(employee,field) else warnings ).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(msg, cell.rowIndex, cell.colIndex))
            else : 
                employee_to_add[field] = converted_val
    return (errors, warnings , wrong_cells)

def valid_employees_data_and_upload(employees : list, force_upload : bool , db : DbDep):
    try :
        errors = []
        warnings = []
        wrong_cells = []
        employees_to_add = []
        roles_per_email = {}
        roles = []

        for line, employee in enumerate(employees):
            emp_errors,  emp_warnigns,  emp_wrong_cells, emp = validate_employee_data(employee)
            if emp_errors : 
                msg = ('/n').join(emp_errors)
                errors.append(f"\nLine {line +1 }: \n{msg}")
            if emp_warnigns : 
                msg = ('/n').join(emp_warnigns)
                warnings.append(f"\nLine {line +1 }: \n{msg}")
            if emp_wrong_cells:
                wrong_cells.extend(emp_wrong_cells)

            employees_to_add.append(models.employee(**emp.__dict__))
            roles_per_email[emp.get('email')] = emp.get('roles', [])
            roles.append(emp.get('roles', []))
        
        for field in unique_fields : 
            values = set()
            for line, employee in enumerate(employees):
                cell = employee.get(field)
                val = cell.value.strip()
                if val == '': # if it's mandatory , email and number were alredy checked in fields check
                    continue 
                if val in values :
                    mas = f"{possible_fields} should be unique. but this value exists more than one time in the file"
                    (errors if is_field_mandatory(employee , field ) else warnings).append(msg)
                    wrong_cells.append(schemas.MatchyCell(msg, cell.rowIndex, cell.colIndex))
                else : 
                    values.add(val)
                duplicated_vals = db.query(models.Employee).filter(unique_fields[field]._in(values)).all()
                
                if duplicated_vals:
                    msg = f"{possible_fields[field]} should be unique. {(', ').join(duplicated_vals)} already exist in database"
                    (errors if is_field_mandatory(employee, field)else warnings).append(msg)
                    wrong_cells.append(schemas.MatchyCell(msg, cell.rowIndexn, cell.colIndex))
            
        if errors or (warnings and not force_upload): 
            return schemas.ImportResponse(
                errors = ('\n').join(errors),
                warnings = ('\n').join(warnings),
                wrongCells = wrong_cells
            )
    

        db.add_all(employees_to_add)
        db.flush()
        #add roles for employees 
        db.add_all([[models.Employee(employee_id=id,role=role)for role in roles_per_email[emp.email]] for emp in employees_to_add])

        db.commit()
    except Exception as e : 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500 , detail = get_error_message(str(e)) )
    
    return schemas.ImportResponse(
            detail = "file uploaded",
            status_code = 201
    )

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



@app.post("/employees/import")
def imporEmployess():
    pass

@app.get("/employees/possibleImportFields")
def getPossibleFilds(db:DbDep):
    return schemas.ImportPossibleFields(
        possible_fields= options,
    )

@app.post('employees/csv')
def upload(entry: schemas.MatchyUploadEntry, db : DbDep):
    employees = entry.lines
    if not employees :
        raise HTTPException(status_code = 400, detail = "Nothing to do, empty file")
    
    missing_mandatory_fields = set(mandatory_fields.keys()) - set(employees[0].keys())
    if missing_mandatory_fields:
        raise HTTPException(
            status_code = 400, 
            detail = f"missing mandatory fields : {(', ').join([display for fiels, display in missing_mandatory_fields.items()])}"
        )
     
    return valid_employees_data_and_upload(employees, entry.forceUpload,db)
    
    
    


    





