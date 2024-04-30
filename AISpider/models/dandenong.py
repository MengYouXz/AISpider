from sqlalchemy import Column, String, Text, Integer, DateTime, func
from .metadata_base import Base

class Dandenong(Base):
    __tablename__ = 'dandenong'
    id = Column(Integer, primary_key=True)
    
    applicationid = Column(String(128), nullable=False, unique=True)
    category = Column(String(512), nullable=True)
    subcategory = Column(String(512), nullable=True)
    word = Column(String(512), nullable=True)
    description = Column(String(512), nullable=True)
    lodged = Column(Integer, nullable=True, server_default=None)  # time
    cost = Column(String(128), nullable=True)
    decision = Column(String(512), nullable=True)
    required = Column(String(512), nullable=True)
    commenced = Column(String(512), nullable=True)
    meetingdate = Column(Integer, nullable=True, server_default=None)  # time
    authdecision = Column(String(512), nullable=True)
    authdecisiondate = Column(Integer, nullable=True, server_default=None) # time
    vcatappeallodgeddate = Column(Integer, nullable=True, server_default=None) # time
    vcatdecisiondate = Column(Integer, nullable=True, server_default=None)  # time
    vcatdecision = Column(String(512), nullable=True)
    correctiondecision = Column(String(512), nullable=True)
    applicationamended = Column(String(512), nullable=True)
    finaloutcome = Column(String(512), nullable=True)
    finaloutcomedate = Column(Integer, nullable=True, server_default=None) # time
    lodgedplannumber = Column(String(512), nullable=True)
    plancertified = Column(Integer, nullable=True, server_default=None)  # time
    planrecertified = Column(String(512), nullable=True)
    statementcompliance = Column(Integer, nullable=True, server_default=None)
    address = Column(Text, nullable=True)
    documents = Column(String(512), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())