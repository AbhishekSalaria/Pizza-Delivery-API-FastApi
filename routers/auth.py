import sys
sys.path.append("..")

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWSError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

models.Base.metadata.create_all(bind=engine)

SECRET_KEY = "ghgg42jGH9kh8GKgDFDIF9Nah9d8kH6DF4O2D"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Signup(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool
    is_staff: bool

router = APIRouter(
    prefix="/api",
    tags=["Authentication"],
    responses={401:{"user":"Not Authorized"}}
)

def create_access_token(user_id: int, username: str, 
                        expires_delta: Optional[timedelta] = None):
    encode =  {"sub":username,"id":user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp":expire})
    return  jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)    

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return unsuccessful_response(401)
        return {"username":username, "id": user_id}
    except JWSError:
        return unsuccessful_response(401)

@router.post("/signup")
async def signup(sign_up: Signup,db: Session = Depends(get_db)):
    sign_up_model = models.User()
    sign_up_model.username = sign_up.username
    sign_up_model.email = sign_up.email
    sign_up_model.password = sign_up.password
    sign_up_model.is_active = sign_up.is_active
    sign_up_model.is_staff = sign_up.is_staff

    db.add(sign_up_model)
    db.commit()
    
    return successful_response(201)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    user = db.query(models.User)\
        .filter(models.User.username == form_data.username)\
        .filter(models.User.password == form_data.password).first()
    if not user:
        return unsuccessful_response(401)
    
    token = create_access_token(user.id,user.username, timedelta(minutes=20))
    return {"token":token}

def unsuccessful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Failure'
    }    

def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }