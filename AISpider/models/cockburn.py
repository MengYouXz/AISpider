from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Cockburn(Base):
    __tablename__ = 'cockburn'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_number = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True, server_default=None)
    group_ = Column(String(255), nullable=True, server_default=None)
    category = Column(String(255), nullable=True, server_default=None)
    sub_category = Column(String(255),nullable=True, server_default=None)
    status_ = Column(String(255),nullable=True, server_default=None)
    lodgement_date = Column(Integer, nullable=True, server_default=None)
    stage = Column(Text, nullable=True, server_default=None)

    address = Column(Text, nullable=True, server_default=None)
    
    document = Column(Text, nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
