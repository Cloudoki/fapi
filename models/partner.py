from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship, backref
from models.base import Base

class Partner(Base):
    __tablename__ = 'partners'

    uid = Column(String(64))
    name = Column(String(128))
    meta = Column(Text)
