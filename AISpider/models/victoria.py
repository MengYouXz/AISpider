from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class town_of_victoria_park(Base):
    __tablename__ = 'town_of_victoria_park'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(255), nullable=False, unique=True)
    app_location = Column(String(255), nullable=False, unique=True)
    app_data_post = Column(Integer,nullable=True, server_default=None)
    app_data_closing = Column(Integer, nullable=True, server_default=None)
    app_detail_text = Column(Text,nullable=True,server_default=None)
    people_name = Column(String(255),nullable=True, server_default=None)
    people_office = Column(String(255),nullable=True, server_default=None)
    people_phone = Column(String(255),nullable=True, server_default=None)
    people_email = Column(String(255),nullable=True, server_default=None)
    documents = Column(Text,nullable=True, server_default=None)


    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
