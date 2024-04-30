from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base

class Armadale(Base):
    __tablename__ = 'armadale'
    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False, unique=True)
    feedback_closes = Column(String(512), nullable=True)
    address = Column(String(512), nullable=True)
    text = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())