# app/dependencies.py
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError

# Secret key and algorithm for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


# ----------------------------
# Verify and decode JWT token
# ----------------------------
def verify_token(authorization: str = Header(...)):
    """
    Verify JWT token from Authorization header.
    Header must be: "Authorization: Bearer <token>"
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ----------------------------
# Get current logged-in user
# ----------------------------
def get_current_user(user: dict = Depends(verify_token)):
    """
    Dependency to get current logged-in user
    """
    return user


# ----------------------------
# Admin-only access
# ----------------------------
def admin_only(user: dict = Depends(get_current_user)):
    """
    Dependency to allow only admins
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
