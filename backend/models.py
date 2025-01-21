from sqlalchemy import Column, String,Integer
from sqlalchemy.ext.declarative import declarative_base

from database import Base


class moveit(Base):
    __tablename__ = 'moveit'
    id = Column(Integer, primary_key=True)
    Div = Column(String(255))
    Addys = Column(String(255))
    Ship = Column(String(255))
    AID = Column(String(255))
    Pcs = Column(String(255))
    Weight = Column(String(255))
    Carriers = Column(String(255))
    Pickup = Column(String(255))
    Deliv = Column(String(255))
    Origin = Column(String(255))
    Origin_State = Column(String(255))
    State1 = Column(String(255))
    Zip1 = Column(String(255))
    Destination = Column(String(255))
    State2 = Column(String(255))
    Destination_State = Column(String(255))
    Zip2 = Column(String(255))
