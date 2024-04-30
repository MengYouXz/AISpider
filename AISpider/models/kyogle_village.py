from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class kyogle_villageItem(Base):
    __tablename__ = 'kyogle_village'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(100))
    detail_txt = Column(Text, nullable=True, server_default=None)
    detail_Lodged = Column(Integer, nullable=True, server_default=None)
    detail_Determined = Column(Integer, nullable=True)
    detail_status = Column(String(255), nullable=True)
    # detail_contact = Column(String(255))
    detail_cost = Column(String(255), nullable=True, server_default=None)
    detail_officer = Column(String(255), nullable=True, server_default=None)
    location = Column(String(255), nullable=True, server_default=None)
    people = Column(String(255), nullable=True, server_default=None)

    # estimated_cost = Column(String(20))
    # officer = Column(String(100))
    # location = Column(Text)
    # people = Column(Text)
    # docs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
