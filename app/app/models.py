from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)
    image = Column(String, default="")
    available = Column(Boolean, default=True)


class HotelTable(Base):
    __tablename__ = "hotel_tables"

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    status = Column(String, default="free")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, nullable=False)
    items_json = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pending")
