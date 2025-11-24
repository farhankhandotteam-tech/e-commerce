from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user, get_password_hash, create_access_token, verify_password, get_user_by_email
from app.db import users_col
from app.utils import obj_to_dict


router = APIRouter(tags=['users'])


@router.post('/register')
async def register(payload: dict):
# expected: name, email, password
existing = await get_user_by_email(payload.get('email'))
if existing:
raise HTTPException(status_code=400, detail='Email already registered')
user_doc = {
'name': payload.get('name'),
'email': payload.get('email'),
'password_hash': get_password_hash(payload.get('password')),
'role': 'user',
}
res = await users_col.insert_one(user_doc)
created = await users_col.find_one({'_id': res.inserted_id})
return obj_to_dict(created)


@router.post('/login')
async def login(payload: dict):
# expects email and password
user = await get_user_by_email(payload.get('email'))
if not user:
raise HTTPException(status_code=400, detail='Invalid credentials')
if not verify_password(payload.get('password'), user.get('password_hash')):
raise HTTPException(status_code=400, detail='Invalid credentials')
token = create_access_token({'user_id': user.get('id'), 'role': user.get('role')})
return {'access_token': token, 'token_type': 'bearer'}


@router.get('/user/profile')
async def get_profile(current_user=Depends(get_current_user)):
user = dict(current_user)
user.pop('password_hash', None)
return user


@router.put('/user/profile')
async def update_profile(update: dict, current_u