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

router = APIRouter(
    prefix="/api",
    tags=["SuperUser"],
    responses={401:{"user":"Not Authorized"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class OrderStatus(str,Enum):
    pending = "pending"
    intransit = "in-transit"
    delivered = "delivered"

class UpdateStatus(BaseModel):
    status: OrderStatus

@router.put("/order/status/{order_id}")
async def order_status_update(order_id: int, orderstatus: UpdateStatus,
                db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        is_superuser = db.query(models.User)\
                                .filter(models.User.id == user.get("id"))\
                                .first()
        if is_superuser is None:
            return unsuccessful_response(401)
        if is_superuser.is_staff == False:
            return {"Failure": "Not a Superuser"}

        order_update_model = db.query(models.Order)\
                                .filter(models.Order.id == order_id)\
                                .first()
        
        if order_update_model is None:
            return unsuccessful_response(401)

        order_update_model.order_status = orderstatus.status

        db.add(order_update_model)
        db.commit()

        return successful_response(201)

@router.get("/orders")
async def list_all_orders(db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        is_superuser = db.query(models.User)\
                                .filter(models.User.id == user.get("id"))\
                                .first()
        if is_superuser is None:
            return unsuccessful_response(401)
        if is_superuser.is_staff == False:
            return {"Failure": "Not a Superuser"}

        order_model = db.query(models.Order).all()
        
        if order_model is None:
            return unsuccessful_response(401)

        return order_model

@router.get("/orders/{order_id}")
async def retrieve_an_order(order_id: int,db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
        if user is None:
            return unsuccessful_response(401)
        is_superuser = db.query(models.User)\
                                .filter(models.User.id == user.get("id"))\
                                .first()
        if is_superuser is None:
            return unsuccessful_response(401)
        if is_superuser.is_staff == False:
            return {"Failure": "Not a Superuser"}

        retrieve_order_model = db.query(models.Order).filter(models.Order.id == order_id).first()
        
        if retrieve_order_model is None:
            return unsuccessful_response(401)

        return retrieve_order_model