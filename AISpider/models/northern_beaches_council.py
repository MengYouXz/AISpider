from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class eservices(Base):
    __tablename__ = 'northern_beaches_council'


    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, nullable=False, unique=True)
    app_num = Column(String(500), nullable=False, unique=True)
    description = Column(Text,nullable=True, server_default=None)
    applicationType = Column(String(255), nullable=True, server_default=None)
    status = Column(String(255),nullable=True,server_default=None)
    submitted = Column(Integer, nullable=True, server_default=None)
    exhibitionPeriod = Column(String(255),server_default=None)
    determined = Column(Integer, nullable=True, server_default=None)
    determination_level = Column(String(255),nullable=True, server_default=None)
    appeal_status = Column(String(255),nullable=True, server_default=None)
    cost = Column(String(255),nullable=True, server_default=None)
    officer = Column(String(255),nullable=True, server_default=None)
    # related = Column(Text,nullable=True, server_default=None)
    location = Column(Text,nullable=True, server_default=None)
    people = Column(Text,nullable=True, server_default=None)
    docs = Column(Text,nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
