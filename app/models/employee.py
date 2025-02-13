from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKey, Integer, String, Date, DateTime, func
from app.enums import Gender,AccountStatus,ContractType
from ..database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    birth_date = Column(Date, nullable=True)
    address = Column(String, nullable = True)
    gender = Column(Enum(Gender), nullable=False)
    phone_number = Column(Integer, nullable=False)
    account_status = Column(Enum(AccountStatus), nullable=False,default=AccountStatus.Inactive)
    contract_type = Column(Enum(ContractType), nullable=False)
    cnss_number = Column(String, nullable=False, unique=True)
    created_on = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(contract_type IN ('Cdi', 'Cdd') AND cnss_number IS NOT NULL AND cnss_number ~ '^\\d{8}-\\d{2}$') "
            "OR (contract_type IN ('Apprenti', 'Sivp') AND (cnss_number IS NULL OR cnss_number ~ '^\\d{8}-\\d{2}$'))",
            name='employee_contract_check'
        ),
    )