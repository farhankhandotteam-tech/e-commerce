from pydantic import BaseModel, EmailStr

class UserRegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
