from sqlalchemy import Column, Integer, String
from Task3.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)
    section = Column(String, index=True)
