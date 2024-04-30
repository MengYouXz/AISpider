from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Hobart(Base):
    __tablename__ = 'hobart_city_council'
    id = Column(Integer, primary_key=True, autoincrement=True)

    app_id = Column(Integer, nullable=False, unique=True)
    app_num = Column(String(255), nullable=False, unique=True)
    app_detail = Column(String(255),nullable=True, server_default=None)
    officer = Column(String(255), nullable=True, server_default=None)
    data_status = Column(String(255),nullable=True)
    app_related = Column(String(255),nullable=True, server_default=None)
    location = Column(String(255),nullable=True, server_default=None)
    documents = Column(Text,nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
