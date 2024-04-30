from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base

class Wollongong(Base):
    __tablename__ = 'wollongong'

    id = Column(Integer, primary_key=True)
    app_number = Column(String(128), nullable=False, unique=True)
    ApplicationType = Column(String(512), nullable=True)
    SiteName = Column(String(512), nullable=True)
    Description = Column(Text, nullable=True)
    Lodged = Column(Integer, nullable=True, server_default=None)
    Accepted = Column(Integer, nullable=True, server_default=None)
    Determined = Column(String(512), nullable=True)
    Effective = Column(Integer, nullable=True, server_default=None)
    ModificationCategory = Column(String(512), nullable=True)
    development = Column(String(512), nullable=True)
    NSWPlanningPortal = Column(String(512), nullable=True)
    notification = Column(String(512), nullable=True)
    dwellinghouse = Column(String(512), nullable=True)
    Lapsed = Column(Integer, nullable=True, server_default=None)
    Completed = Column(Integer, nullable=True, server_default=None)
    progress = Column(Text, nullable=True)
    people = Column(String(512), nullable=True)
    associations = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())