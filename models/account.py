from sqlalchemy import Table, Column, ForeignKey, String, Integer, Text
from sqlalchemy.orm import relationship, backref
from models.base import Base

accounts_subaccounts = Table('accounts_subaccounts', Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id')),
    Column('sub_id', Integer, ForeignKey('accounts.id'))
)

class Account(Base):
    __tablename__ = 'accounts'

    uid = Column(String(64))
    name = Column(String(128))
    meta = Column(Text)

    documents = relationship("Document")
