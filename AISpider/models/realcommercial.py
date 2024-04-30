from sqlalchemy import Column, String, Text, Integer
from .metadata_base import Base


class Realcommercial(Base):
    __tablename__ = 'realcommercial'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_model = Column(String(255), nullable=True, server_default=None)
    app_id = Column(Integer, nullable=False, unique=True)
    location = Column(String(255), nullable=True, server_default=None)
    purpose_to = Column(String(255),nullable=True, server_default=None)
    price_information = Column(String(255), nullable=True, server_default=None)

    land_area = Column(Text,nullable=True)
    floor_area = Column(String(255),nullable=True, server_default=None)
    property_extent = Column(Text,nullable=True, server_default=None)
    tenure_type = Column(String(255),nullable=True, server_default=None)
    car_spaces = Column(String(255),nullable=True, server_default=None)
    parking_info = Column(String(255),nullable=True, server_default=None)
    municipality = Column(String(255),nullable=True, server_default=None)
    sold_on = Column(String(255),nullable=True, server_default=None)
    zoning_ = Column(String(255),nullable=True, server_default=None)

    description = Column(Text,nullable=True, server_default=None)
    people_name = Column(String(255),nullable=True, server_default=None)
    people_address = Column(String(255),nullable=True, server_default=None)

    # created_at = Column(DateTime, server_default=func.now())
    # updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


