from ast import Try
from sqlalchemy import Column, Integer
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
