from typing import Annotated
from fastapi import Depends
from app.main import get_db
from sqlalchemy.orm import Session

DbDep = Annotated[Session, Depends(get_db)]