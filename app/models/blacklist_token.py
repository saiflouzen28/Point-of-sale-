from sqlalchemy import Column, Integer, String
from ..database import Base

class BlacklistToken(Base):
    __tablename__ = "blacklistToken"

    id = Column(Integer, primary_key=True, nullable=False)
    token = Column(String, nullable=False)