from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.api.v1 import user_routes, statement_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Finance Intelligence Platform', version='1.0.0')

# Mount routers
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["user"])
app.include_router(statement_routes.router, prefix="/api/v1/statement", tags=["statement"])

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