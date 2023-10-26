from sqlalchemy import String, Float, UUID, DateTime
from sqlalchemy import Column

from .base_class import Base


class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID, primary_key=True, index=True)
    datetime = Column(DateTime)
    title = Column(String)
    text = Column(String)
    x_avg_count_in_line = Column(Float)
