from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime, func
from app.enums import TokenStatus
from datetime import datetime, UTC
from ..database import Base

class AccountActivation(Base):
    __tablename__ = "accountActivation"

    id = Column(Integer, primary_key=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"),nullable=False)
    email = Column(String, nullable=False)
    token = Column(String, nullable=False)
    create_on = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(Enum(TokenStatus), nullable=False)