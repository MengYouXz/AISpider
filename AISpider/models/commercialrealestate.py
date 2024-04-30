from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Commercialrealestate(Base):
    __tablename__ = 'commercialrealestate'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_number = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True, server_default=None)
    type_ = Column(String(255), nullable=True, server_default=None)

    floor_area = Column(String(255), nullable=True, server_default=None)
    land_area = Column(String(255), nullable=True, server_default=None)
    parking = Column(String(255),nullable=True, server_default=None)
    annual_return = Column(String(255),nullable=True, server_default=None)
    availability = Column(String(255),nullable=True, server_default=None)
    category = Column(String(255),nullable=True, server_default=None)

    address = Column(Text, nullable=True, server_default=None)
    value = Column(String(255), nullable=True, server_default=None)
    agent_info = Column(Text, nullable=True, server_default=None)

    closing_date = Column(Integer, nullable=True, server_default=None)
    recipient_name = Column(String(255),nullable=True, server_default=None)
    delivery_address = Column(String(255),nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
