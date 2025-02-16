from datetime import datetime , timedelta , timezone
from typing import Annotated
from app.crud.employee import get_confirmation_code
from app.crud.error import add_error, get_error_message
from app.schemas import Token
from app.dependencies import DbDep
from fastapi import Depends, APIRouter, HTTPException, status
from app import crud, schemas, models, enums
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas import BaseOut, ConfirmAccount


router = APIRouter(
    tags=["Authentication"],
)
""" 
@router.post("/token")
async def login_for_access_token(
    db: DbDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    employee = authenticate_user(db, form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

 """
@router.patch("/employee1",response_model=BaseOut)
def confirm_account(confirAccountInput : ConfirmAccount,db: DbDep):
    try:
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
    except Exception as e : 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500 , detail = get_error_message(text) )

    return BaseOut(
        detail= "Account confirmed",
        status_code= status.HTTP_200_OK
    )
