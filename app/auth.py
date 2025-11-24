import os
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


class TokenData(BaseModel):
user_id: Optional[str] = None
role: Optional[str] = 'user'


async def get_user_by_email(email: str):
user = await users_col.find_one({'email': email})
return obj_to_dict(user)




def verify_password(plain_password, hashed_password):
return pwd_context.verify(plain_password, hashed_password)




def get_password_hash(password):
return pwd_context.hash(password)




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
to_encode = data.copy()
if expires_delta:
expire = datetime.utcnow() + expires_delta
else:
expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
to_encode.update({'exp': expire})
encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
return encoded_jwt




async def get_current_user(token: str = Depends(oauth2_scheme)):
credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
user_id: str = payload.get('user_id')
role: str = payload.get('role', 'user')
if user_id is None:
raise credentials_exception
token_data = TokenData(user_id=user_id, role=role)
except JWTError:
raise credentials_exception


# Try to fetch user by ObjectId or by string id stored as id
import bson
user = None
try:
user = await users_col.find_one({'_id': bson.ObjectId(user_id)})
except Exception:
# try by string id field if you stored it that way
user = await users_col.find_one({'id': user_id})


if not user:
raise credentials_exception
user = obj_to_dict(user)
return user




async def require_admin(current_user=Depends(get_current_user)):
if current_user.get('role') != 'admin':
raise HTTPException(status_code=403, detail='Admin privileges required')
return current_user