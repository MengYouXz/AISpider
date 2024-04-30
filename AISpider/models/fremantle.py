from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base


class Fremantle(Base):
    __tablename__ = 'city_of_fremantle'

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_num = Column(String(255), nullable=False, unique=True)
    app_detail = Column(Text,nullable=True, server_default=None)
    app_group = Column(String(255),nullable=True, server_default=None)
    app_category = Column(String(255),nullable=True, server_default=None)
    app_sub_category = Column(String(255),nullable=True, server_default=None)
    app_status = Column(String(255),nullable=True, server_default=None)
    lodgement_date = Column(Integer,nullable=True, server_default=None)
    stage_decision = Column(String(255),nullable=True, server_default=None)
    wapc_ref = Column(String(255),nullable=True, server_default=None)
    council_decision = Column(String(255),nullable=True, server_default=None)
    wapc_decision = Column(String(255),nullable=True, server_default=None)
    no_of_lots = Column(String(255),nullable=True, server_default=None)
    date_received = Column(Integer,nullable=True, server_default=None)
    council_decision_date = Column(Integer,nullable=True, server_default=None)
    wapc_decision_date = Column(Integer, nullable=True, server_default=None)
    advertisement_commence = Column(Integer,nullable=True)
    advertisement_closing = Column(Integer,nullable=True, server_default=None)
    decision_date = Column(Integer,nullable=True, server_default=None)
    date_issued = Column(String(255),nullable=True, server_default=None)
    detail_address = Column(String(255),nullable=True, server_default=None)
    detail_address_description = Column(String(255),nullable=True, server_default=None)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

