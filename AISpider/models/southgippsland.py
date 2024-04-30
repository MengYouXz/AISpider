from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .moretonbay import Base


class Southgippsland(Base):
    __tablename__ = 'southgippsland'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_number = Column(String(64), nullable=False, unique=True)
    app_date = Column(Integer, nullable=True, server_default=None)
    app_location = Column(String(256), nullable=True, server_default=None)
    app_type = Column(String(256), nullable=True, server_default=None)
    app_decision = Column(Text, nullable=True, server_default=None)
    status = Column(String(256), nullable=True, server_default=None)
    property_address = Column(Text, nullable=True, server_default=None)
    
    app_task_type = Column(String(256), nullable=True, server_default=None)
    actual_started_date = Column(Integer, nullable=True, server_default=None)
    actual_completed_date =Column(Integer, nullable=True, server_default=None)

    app_proposal = Column(Text, nullable=True, server_default=None)
    responsible_officer = Column(String(256), nullable=True, server_default=None)
    alternate_property_address = Column(String(256), nullable=True, server_default=None)
    document = Column(Text, nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
