from sqlalchemy import Column, String, Text, Integer, DateTime, func, UniqueConstraint
from .metadata_base import Base


class LithgowDowns(Base):
    __tablename__ = 'lithgow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True, server_default=None)
    application_group = Column(String(255),nullable=True,server_default=None)
    category = Column(String(255),nullable=True,server_default=None)
    sub_category = Column(String(100),nullable=True,server_default=None)
    lodged_date = Column(Integer, nullable=True, server_default=None)
    stage = Column(String(100),nullable=True,server_default=None)
    determined_date = Column(Integer, nullable=True, server_default=None)
    name_details =Column(Text, nullable=True, server_default=None)
    properties = Column(Text, nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
