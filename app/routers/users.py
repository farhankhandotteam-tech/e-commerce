from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.database import users_collection
from app.models.user import UserRegisterModel, UserLogin
router = APIRouter(prefix="/users", tags=["Users"])

SECRET_KEY = "YOURSECRETKEY123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- REGISTER ----------------
@router.post("/register")
def register_user(data: UserRegisterModel):
    # Check if user already exists
   exist = users_collection.find_one({"email": data.email})
   users_collection.insert_one(user_data)
   if exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Truncate password to 72 bytes to avoid bcrypt error
   safe_password = data.password[:72]

    # Hash password
   hashed_pass = pwd_context.hash(safe_password)

   user_data = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pass,
        "user_role": data.user_role
    }

   users_collection.insert_one(user_data)

   return {"message": "User registered successfully"}



# ---------------- LOGIN ----------------
@router.post("/login")
def login_user(data: UserLogin):

    user = users_collection.find_one({"email": data.email})

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    token_data = {
        "email": user["email"],
        "role": user["user_role"],
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    # Convert exp to timestamp
    token_data["exp"] = int(token_data["exp"].timestamp())

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "Login successful",
        "token": token,
        "user_role": user["user_role"]
    }
