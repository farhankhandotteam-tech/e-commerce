from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models import UserCreate, UserOut
from db import db
from utils import hash_password, verify_password, create_access_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register', response_model=UserOut)
async def register(user: UserCreate):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    doc = {"email": user.email, "hashed_password": hashed, "full_name": user.full_name, "is_admin": False}
    res = await db.users.insert_one(doc)
    doc['id'] = str(res.inserted_id)
    return {"id": doc['id'], "email": doc['email'], "full_name": doc['full_name'], "is_admin": doc['is_admin']}

@router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get('hashed_password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    user_id = str(user['_id'])
    access_token = create_access_token(user_id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/me', response_model=UserOut)
async def me(current_user=Depends(lambda: None)):
    # client should call /auth/me with Authorization header; default dependency overridden in main router registration
    return current_user