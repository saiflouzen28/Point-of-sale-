from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from .config import settings


    #mail_username : settings.mail_username
    #mail_password : settings.mail_password
    #mail_from : settings.mail_from
    #mail_server = settings.mail_server

conf = ConnectionConfig(
    MAIL_USERNAME="test_user",            # Placeholder username
    #MAIL_USERNAME=settings.mail_username
    MAIL_PASSWORD="test_pass",            # Placeholder password
    #MAIL_PASSWORD=settings.mail_password
    MAIL_FROM="test@example.com",         # Placeholder email
    #MAIL_FROM=settings.mail_from
    MAIL_PORT=1025,                       # Change port to 10 for MailHog
    MAIL_SERVER="localhost",              # Use "localhost" for MailHog or Papercut
    #MAIL_SERVER=settings.mail_server
    MAIL_STARTTLS=False,                  # Disable STARTTLS for local server
    MAIL_SSL_TLS=False,                   # Disable SSL/TLS for local server
    USE_CREDENTIALS=False,                # Set to False as MailHog doesn't require credentials
    VALIDATE_CERTS=False,                  # Set to False for local development
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)


async def simple_send(emails: List[EmailStr], body: dict) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=emails,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)

    await fm.send_message(message, template_name="account_activation.html")
    
    return JSONResponse(status_code=200, content={"message": "email has been sent"})   