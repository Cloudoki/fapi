from sqlalchemy.ext.declarative import DeclarativeMeta, as_declarative, declared_attr
from sqlalchemy import Column, Integer
from collections import OrderedDict

# Base = declarative_base()

@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    RELATIONSHIPS_TO_DICT = True

    id = Column(Integer, primary_key=True)

    def __iter__(self):
        return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]
        return res



# class Base(D):
#     def __iter__(self):
#         return self.to_dict().iteritems()
#
#     def to_dict(self, rel=None, backref=None):
#         if rel is None:
#             rel = self.RELATIONSHIPS_TO_DICT
#         res = {column.key: getattr(self, attr)
#                for attr, column in self.__mapper__.c.items()}
#         if rel:
#             for attr, relation in self.__mapper__.relationships.items():
#                 # Avoid recursive loop between to tables.
#                 if backref == relation.table:
#                     continue
#                 value = getattr(self, attr)
#                 if value is None:
#                     res[relation.key] = None
#                 elif isinstance(value.__class__, DeclarativeMeta):
#                     res[relation.key] = value.to_dict(backref=self.__table__)
#                 else:
#                     res[relation.key] = [i.to_dict(backref=self.__table__)
#                                          for i in value]
#         return res
