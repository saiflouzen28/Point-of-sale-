from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKey, Integer, String, Date, DateTime, func
from app.enums import Gender,AccountStatus,ContractType
from ..database import Base

class Erorr(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False , server_default=func.now())

    