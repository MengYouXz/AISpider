from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class maribyrnong(Base):
    __tablename__ = 'maribyrnong_city_council'
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_num = Column(String(100), nullable=False,unique=True)
    app_tittle = Column(Text, nullable=True, server_default=None)
    proposal = Column(Text, nullable=True, server_default=None)
    notes = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    related_information = Column(Text, nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
