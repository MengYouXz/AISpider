from sqlalchemy import Column, String, Text, Integer
from .metadata_base import Base


class domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_model = Column(String(255), nullable=True, server_default=None)
    app_id = Column(Integer, nullable=False, unique=True)
    location = Column(String(255), nullable=True, server_default=None)
    app_title = Column(String(255),nullable=True, server_default=None)
    app_status = Column(String(255),nullable=True, server_default=None)
    purpose_to = Column(String(255), nullable=True, server_default=None)
    property_features = Column(Text,nullable=True, server_default=None)

    count_beds = Column(String(255),nullable=True, server_default=None)
    count_baths = Column(String(255),nullable=True, server_default=None)
    parking_info = Column(String(255),nullable=True, server_default=None)
    land_area = Column(String(255),nullable=True, server_default=None)


    description = Column(Text,nullable=True, server_default=None)
    domain_says = Column(String(255),nullable=True, server_default=None)
    people_name = Column(String(255),nullable=True, server_default=None)
    people_address = Column(String(255),nullable=True, server_default=None)

    total_title = Column(String(255),nullable=True, server_default=None)
    total_location = Column(String(255),nullable=True, server_default=None)
    total_information = Column(String(255),nullable=True, server_default=None)
    project_highlights = Column(Text,nullable=True, server_default=None)
    total_description = Column(Text,nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
