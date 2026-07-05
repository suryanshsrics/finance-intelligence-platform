from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.api.v1 import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Finance Intelligence Platform', version='1.0.0')

# Mount routers
app.include_router(users.router, prefix="/api/v1/users", tags=["user-create-api"])

@app.get("/")
def root():
    return {
        "message": "Finance Intelligence Platform is running"
    }

@app.get("/health")
def health_check():
    return {
        "message": "The application is healthy. Lay back and relax."
    }