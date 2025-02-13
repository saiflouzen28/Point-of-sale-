from sqlalchemy import Column, Enum, ForeignKey, Integer
from app.enums import RoleType
from ..database import Base

class EmployeeRole(Base):
    __tablename__ = "employeeRole"

    id = Column(Integer, primary_key=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"),nullable=False)
    role = Column(Enum(RoleType), nullable=False)



