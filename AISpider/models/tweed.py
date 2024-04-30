from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class TWEED(Base):
    __tablename__ = 'tweed_shire_council'


    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, nullable=False, unique=True)
    app_num = Column(String(500), nullable=False, unique=True)
    detail_text = Column(Text,nullable=True, server_default=None)
    detail_Lodged_data = Column(Integer, nullable=True, server_default=None)
    detail_Determined_data = Column(String(255),nullable=True)
    detail_cost = Column(String(255),nullable=True, server_default=None)
    detail_officer = Column(String(255),nullable=True, server_default=None)
    location = Column(String(255),nullable=True, server_default=None)
    people_Applicant = Column(String(255),nullable=True, server_default=None)
    documents_url = Column(Text,nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
