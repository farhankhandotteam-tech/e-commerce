from fastapi import APIRouter, HTTPException
from models.user import UserRegister, UserLogin
from database import users_col
from auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    if users_col.find_one({"email": user.email}):
        raise HTTPException(400, "User already exists")
    user_dict = user.dict()
    user_dict["password"] = hash_password(user.password)
    result = users_col.insert_one(user_dict)
    return {"msg": "User registered", "id": str(result.inserted_id)}

@router.post("/login")
def login(user: UserLogin):
    db_user = users_col.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"_id": str(db_user["_id"]), "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}
