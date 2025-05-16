from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import os

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth.auth_utils import (
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialize FastAPI app
app = FastAPI(
    title="QuantumNest Capital API",
    description="Backend API for QuantumNest Capital platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "Welcome to QuantumNest Capital API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
from app.api import users, portfolio, market, ai, blockchain, admin

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(market.router, prefix="/market", tags=["market"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
