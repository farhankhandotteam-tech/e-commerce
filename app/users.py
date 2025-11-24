# app/users.py
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import (
    get_current_user,
    get_password_hash,
    create_access_token,
    verify_password,
    get_user_by_email,
)
from app.db import users_col
from app.utils import obj_to_dict

router = APIRouter(tags=["users"])


def _sanitize_user_for_response(user: Dict) -> Dict:
    """
    Convert _id -> str and remove password_hash before returning to client.
    """
    if not user:
        return user
    user = obj_to_dict(user.copy())
    user.pop("password_hash", None)
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: Dict):
    """
    Register a new user.
    Expects payload to contain: name, email, password
    """
    # basic validation
    name = payload.get("name")
    email = payload.get("email")
    password = payload.get("password")

    if not name or not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name, email and password are required",
        )

    # check existing user
    existing = await get_user_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_doc = {
        "name": name,
        "email": email,
        "password_hash": get_password_hash(password),
        "role": "user",
    }

    res = await users_col.insert_one(user_doc)
    created = await users_col.find_one({"_id": res.inserted_id})
    return _sanitize_user_for_response(created)


@router.post("/login")
async def login(payload: Dict):
    """
    Login: returns access token.
    Expects payload to contain: email, password
    """
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email and password are required",
        )

    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    if not verify_password(password, user.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    # create token payload using user_id claim (string), matches auth.require_admin
    user_id_str = str(user.get("_id"))
    token = create_access_token({"user_id": user_id_str, "role": user.get("role")})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/user/profile")
async def get_profile(current_user: Dict = Depends(get_current_user)):
    """
    Returns the current user's profile (no password_hash).
    Assumes get_current_user returns the user document from DB.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return _sanitize_user_for_response(current_user)


@router.put("/user/profile")
async def update_profile(update: Dict, current_user: Dict = Depends(get_current_user)):
    """
    Update current user's profile.
    Accepts any of: name, email, password
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = current_user.get("_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user")

    update_payload: Dict = {}
    name = update.get("name")
    email = update.get("email")
    password = update.get("password")

    if name:
        update_payload["name"] = name

    if email:
        # if user is changing email, ensure it's not already used by someone else
        existing = await get_user_by_email(email)
        if existing and str(existing.get("_id")) != str(user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        update_payload["email"] = email

    if password:
        update_payload["password_hash"] = get_password_hash(password)

    if not update_payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")

    res = await users_col.update_one({"_id": user_id}, {"$set": update_payload})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated = await users_col.find_one({"_id": user_id})
    return _sanitize_user_for_response(updated)
