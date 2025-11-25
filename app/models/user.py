from pydantic import BaseModel, EmailStr

class UserRegisterModel(BaseModel):
   class UserRegisterModel(BaseModel):
    name: str
    email: str
    password: constr(max_length=72)   # <= 72 characters
    user_role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
