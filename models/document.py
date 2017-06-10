from sqlalchemy import Column, DateTime, String, Integer, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from models.base import Base
from models.tag import tags_documents
# from models.account import Account
# from models.partner import Partner

class Document(Base):
    __tablename__ = 'documents'

    uid = Column(String(128))
    name = Column(String(128))
    value = Column(Float)
    meta = Column(Text)

    date = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    account_id = Column(Integer, ForeignKey('accounts.id'))
    partner_id = Column(Integer, ForeignKey('partners.id'))

    account = relationship(
        "Account",
        backref=backref('accounts',
                         uselist=True,
                         cascade='delete,all'))

    partner = relationship(
        "Partner",
        backref=backref('partners',
                         uselist=True,
                         cascade='delete,all'))

    tags = relationship(
        "Tag",
        secondary=tags_documents,
        back_populates="documents")
