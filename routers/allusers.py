import sys
sys.path.append("..")

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from .auth import unsuccessful_response, successful_response, get_current_user

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class PizzaSizes(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    extralarge = "extra-large"

class OrderValues(BaseModel):
    quantity: int
    pizza_size: PizzaSizes
    flavour: str

router = APIRouter(
    prefix="/api",
    tags=["All Users"],
    responses={401:{"user":"Not Authorized"}}
)

@router.post("/order")
async def Order(order: OrderValues, db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        order_model = models.Order()
        order_model.quantity = order.quantity
        order_model.pizza_size = order.pizza_size
        order_model.flavour = order.flavour
        order_model.order_status = "pending"
        order_model.user_id = user.get("id")

        db.add(order_model)
        db.commit()

        return successful_response(200)

@router.put("/order/update/{order_id}")
async def order_update(order_id: int, order: OrderValues,
                db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        order_update_model = db.query(models.Order)\
                                .filter(models.Order.id == order_id)\
                                .filter(models.Order.user_id == user.get("id"))\
                                .first()
        if order_update_model is None:
            return unsuccessful_response(401)
        order_update_model.quantity = order.quantity
        order_update_model.pizza_size = order.pizza_size
        order_update_model.flavour = order.flavour
        order_update_model.order_status = "pending"
        order_update_model.user_id = user.get("id")

        db.add(order_update_model)
        db.commit()

        return successful_response(201)
    
@router.delete("/order/delete/{order_id}")
async def order_delete(order_id: int,
                db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        order_delete_model = db.query(models.Order)\
                                .filter(models.Order.id == order_id)\
                                .filter(models.Order.user_id == user.get("id"))\
                                .first()     
        if order_delete_model is None:
            return unsuccessful_response(401)

        db.query(models.Order).filter(models.Order.id == order_id)\
            .filter(models.Order.user_id == user.get("id")).delete()
        
        db.commit()

        return successful_response(201)

@router.get("/user/orders")
async def get_user_orders(db: Session = Depends(get_db),
                          user: dict = Depends(get_current_user)):
        
        if user is None:
            return unsuccessful_response(401)
        return db.query(models.Order).filter(models.Order.user_id == user.get("id")).all()

@router.get("/user/order/{order_id}")
async def get_user_specific_orders(order_id:int,db: Session = Depends(get_db),
                          user: dict = Depends(get_current_user)):
        
        if user is None:
            return unsuccessful_response(401)
        return db.query(models.Order)\
            .filter(models.Order.user_id == user.get("id"))\
            .filter(models.Order.id == order_id)\
            .first()