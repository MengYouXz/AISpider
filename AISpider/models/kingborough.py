from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class kingborough(Base):
    __tablename__ = 'kingborough'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_num = Column(String(255), nullable=False, unique=True)
    app_address = Column(String(255), nullable=True, server_default=None)
    advertised_date = Column(Integer,nullable=True, server_default=None)
    closing_date = Column(Integer, nullable=True, server_default=None)
    purpose = Column(String(255),nullable=True)
    documents = Column(Text,nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
