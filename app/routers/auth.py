from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from db import db
from utils import hash_password, verify_password, create_access_token
from bson import ObjectId
from models import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register_user(payload: UserCreate):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password": hash_password(payload.password),
        "role": "user",
        "created_at": None
    }
    res = await db.users.insert_one(user_doc)
    token = create_access_token({"sub": str(res.inserted_id)})
    return {"message": "User registered", "token": token}

@router.post("/login")
async def login_user(payload: LoginModel):
    user = await db.users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["_id"])})
    return {"message": "Login successful", "token": token}

@router.get("/me")
async def me(current_user=Depends(lambda: None)):
    """
    Placeholder for docs; actual dependency injection handled in main usage.
    We'll replace via dependency injection in the router include at runtime if desired.
    """
    return {"detail": "Use /auth/me with token header via auth dependency configured in your routes"}
