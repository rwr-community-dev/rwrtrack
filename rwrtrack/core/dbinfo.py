from sqlalchemy import Column, Integer
from sqlalchemy.ext.hybrid import hybrid_property

from .db import DeclarativeBase


class DbInfo(DeclarativeBase):
    __tablename__ = "_dbinfo"
    _id = Column(Integer, primary_key=True)
    _first_date = Column("first_date", Integer, nullable=False)
    _latest_date = Column("latest_date", Integer, nullable=False)

    def __init__(self, date):
        self._first_date = date
        self._latest_date = date

    @hybrid_property
    def first_date(self):
        return self._first_date

    @hybrid_property
    def latest_date(self):
        return self._latest_date

    @latest_date.setter
    def latest_date(self, value):
        self._latest_date = value

    def __repr__(self):
        return f"DbInfo(first_date={self.first_date}, " \
               f"latest_date={self.latest_date})"