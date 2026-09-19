from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.api.v1 import dashboard_routes, user_routes, statement_routes

# Ensure database tables exist before serving requests.
Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance.
app = FastAPI(title='Finance Intelligence Platform', version='1.0.0')

# Mount routers
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["user"])
app.include_router(statement_routes.router, prefix="/api/v1/statement", tags=["statement"])
app.include_router(dashboard_routes.router)

@app.get("/")
def root():
    # Simple endpoint for confirming the service is running.
    return {
        "message": "Finance Intelligence Platform is running"
    }

@app.get("/health")
def health_check():
    # Lightweight health probe for monitoring systems.
    return {
        "message": "The application is healthy. Lay back and relax."
    }
