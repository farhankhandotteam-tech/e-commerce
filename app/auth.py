from passlib.hash import bcrypt as bcrypt_hash
from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str):
    truncated_password = password.encode("utf-8")[:72]
    return bcrypt_hash.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str):
    truncated_password = plain_password.encode("utf-8")[:72]
    return bcrypt_hash.verify(truncated_password, hashed_password)

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
