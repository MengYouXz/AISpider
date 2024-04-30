from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base



class Gosnells(Base):
    __tablename__ = 'city_of_gosnells'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_id = Column(Integer, nullable=False, unique=True)
    app_num = Column(String(255), nullable=False, unique=True)
    app_detail = Column(String(255),nullable=True, server_default=None)
    status = Column(String(255),nullable=True, server_default=None)
    lodged_time = Column(Integer,nullable=True, server_default=None)
    determined_time = Column(Integer,nullable=True, server_default=None)
    app_outcome = Column(String(255),nullable=True, server_default=None)
    officer = Column(String(255), nullable=True, server_default=None)
    location = Column(String(255),nullable=True)
    description_detail = Column(Text,nullable=True, server_default=None)
    people = Column(String(255),nullable=True, server_default=None)
    app_related = Column(String(255),nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
