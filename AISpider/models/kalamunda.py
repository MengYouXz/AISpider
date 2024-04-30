from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Kalamunda(Base):
    __tablename__ = 'kalamunda'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(255), nullable=True,)

    app_number = Column(String(255), nullable=False, unique=True)
    lodgement_date = Column(Integer, nullable=True, server_default=None)
    description = Column(Text, nullable=True, server_default=None)
    applicant = Column(Text, nullable=True, server_default=None)
    
    name = Column(String(255), nullable=True,server_default=None)
    telephone = Column(String(255), nullable=True, server_default=None)
    email = Column(Text, nullable=True, server_default=None)
    
    decision = Column(String(255), nullable=True, server_default=None)
    decision_date = Column(String(255), nullable=True, server_default=None)
    
    stage_ = Column(String(255), nullable=True, server_default=None)
    start_date = Column(String(255), nullable=True, server_default=None)
    end_date = Column(String(255), nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
