from fastapi import FastAPI
import models
from database import engine
from routers import allusers, superuser,auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(allusers.router)
app.include_router(superuser.router)