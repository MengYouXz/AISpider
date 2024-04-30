from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Swan(Base):
    __tablename__ = 'swan'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_number = Column(String(256), nullable=False, unique=True)

    app_type = Column(String(256), nullable=True, server_default=None)
    app_description = Column(String(256), nullable=True, server_default=None)
    status = Column(String(256), nullable=True, server_default=None)
    lodged = Column(Integer, nullable=True, server_default=None)
    app_location = Column(String(256), nullable=True, server_default=None)
    
    pro_adderss =Column(String(256), nullable=True, server_default=None)
    pro_type =Column(String(256), nullable=True, server_default=None)
    pro_ward = Column(String(256), nullable=True, server_default=None)
    land_area = Column(String(256), nullable=True, server_default=None)
    

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

