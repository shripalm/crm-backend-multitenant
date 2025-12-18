import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum 
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base
from enum import Enum as PyEnum

class CompanySizeEnum(str, PyEnum):
    EMP_1_10 = "1-10 employees"
    EMP_11_50 = "11-50 employees"
    EMP_51_200 = "51-200 employees"
    EMP_201_500 = "201-500 employees"
    EMP_500_PLUS = "500+ employees"

class CompanyInfo(Base):
    __tablename__ = "company_info"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    company_size = Column(SAEnum(CompanySizeEnum, name="company_size"), nullable=False)
    description = Column(Text, nullable=True)