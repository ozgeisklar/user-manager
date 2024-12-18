from fastapi import FastAPI
from app.routers.user_api import user_router
from app.routers.auth_api import auth_router
from db.database import create_tables

create_tables()

app = FastAPI(debug=True)

app.include_router(user_router)
app.include_router(auth_router)
