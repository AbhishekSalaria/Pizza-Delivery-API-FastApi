from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer,primary_key = True, index = True)
    username = Column(String, unique = True, index = True)
    email = Column(String, unique = True, index = True)
    password = Column(String)
    is_active = Column(Boolean, default = True)
    is_staff = Column(Boolean, default = False)

    order = relationship("Order",back_populates="owner")

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key = True, index = True)
    quantity = Column(Integer)
    order_status = Column(String)
    pizza_size = Column(String)
    flavour = Column(String)
    user_id = Column(Integer,ForeignKey("user.id"))

    owner = relationship("User",back_populates="order")
    
