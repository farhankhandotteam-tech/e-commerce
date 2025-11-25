from pydantic import BaseModel, EmailStr, constr

class UserRegisterModel(BaseModel):
    name: str
    email:EmailStr
    password: constr(max_length=72)   
    user_role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
