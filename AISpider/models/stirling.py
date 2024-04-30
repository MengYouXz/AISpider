from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Stirling(Base):
    __tablename__ = 'city_of_stirling'

    id = Column(Integer, primary_key=True, autoincrement=True)

    app_num = Column(String(255), nullable=False, unique=True)
    description = Column(Text,nullable=True, server_default=None)
    primary_group = Column(String(255), nullable=True, server_default=None)
    group_ = Column(String(255),nullable=True,server_default=None)
    primary_category = Column(String(255),nullable=True, server_default=None)
    category = Column(String(255),nullable=True, server_default=None)
    sub_category = Column(String(255),nullable=True, server_default=None)
    stage_decision = Column(String(255),nullable=True, server_default=None)
    estimated_cost = Column(String(255),nullable=True, server_default=None)
    formatted_address = Column(String(255),nullable=True, server_default=None)
    suburb = Column(String(255),nullable=True, server_default=None)
    street = Column(String(255),nullable=True, server_default=None)
    initial_target = Column(Integer,nullable=True, server_default=None)
    current_target = Column(Integer,nullable=True, server_default=None)
    status = Column(String(255),nullable=True, server_default=None)
    year = Column(String(255),nullable=True, server_default=None)
    charge_balance = Column(String(255),nullable=True, server_default=None)
    house_No = Column(String(255),nullable=True, server_default=None)
    property_name = Column(String(255),nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

