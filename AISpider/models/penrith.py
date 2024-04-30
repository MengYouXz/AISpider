from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Penrith(Base):
    __tablename__ = 'penrith'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_number = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True, server_default=None)
    category = Column(String(255), nullable=True, server_default=None)
    status = Column(String(255), nullable=True, server_default=None)
    lodged = Column(Integer, nullable=True, server_default=None)
    estimated_cost = Column(String(255), nullable=True, server_default=None)
    officer = Column(String(255), nullable=True, server_default=None)
    decision = Column(Text, nullable=True, server_default=None)
    location = Column(Text, nullable=True, server_default=None)
    documents = Column(Text, nullable=True, server_default=None)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
