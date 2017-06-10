from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship, backref
from models.base import Base

tags_documents = Table('tags_documents', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('document_id', Integer, ForeignKey('documents.id'))
)

class Tag(Base):
    __tablename__ = 'tags'

    slug = Column(String(64), nullable=False, unique=True)
    name = Column(String(255))

    documents = relationship(
        "Document",
        secondary=tags_documents,
        back_populates="tags")
