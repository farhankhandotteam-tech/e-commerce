from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db import products_col, orders_col, users_col
from app.models import ProductIn, ProductOut
from app.auth import require_admin
from app.utils import obj_to_dict


router = APIRouter(prefix='/admin', tags=['admin'])


@router.post('/products', dependencies=[Depends(require_admin)], response_model=ProductOut)
async def create_product(product: ProductIn):
doc = product.dict()
res = await products_col.insert_one(doc)
new = await products_col.find_one({'_id': res.inserted_id})
return obj_to_dict(new)


@router.put('/products/{product_id}', dependencies=[Depends(require_admin)], response_model=ProductOut)
async def update_product(product_id: str, product: ProductIn):
import bson
try:
oid = bson.ObjectId(product_id)
except Exception:
raise HTTPException(status_code=400, detail='Invalid product id')
await products_col.update_one({'_id': oid}, {'$set': product.dict()})
updated = await products_col.find_one({'_id': oid})
return obj_to_dict(updated)


@router.delete('/products/{product_id}', dependencies=[Depends(require_admin)])
async def delete_product(product_id: str):
import bson
try:
oid = bson.ObjectId(product_id)
except Exception:
raise HTTPException(status_code=400, detail='Invalid product id')
res = await products_col.delete_one({'_id': oid})
if res.deleted_count == 0:
raise HTTPException(status_code=404, detail='Product not found')
return {'detail': 'Product deleted'}


@router.get('/orders', dependencies=[Depends(require_admin)])
async def list_orders():
orders = []
async for o in orders_col.find():
orders.append(obj_to_dict(o))
return orders


@router.put('/orders/{order_id}/status', dependencies=[Depends(require_admin)])
async def update_order_status(order_id: str, status: str):
import bson
try:
oid = bson.ObjectId(order_id)
except Exception:
raise HTTPException(status_code=400, detail='Invalid order id')
res = await orders_col.update_one({'_id': oid}, {'$set': {'status': status}})
if res.matched_count == 0:
raise HTTPException(status_code=404, detail='Order not found')
updated = await orders_col.find_one({'_id': oid})
return obj_to_dict(updated)


@router.get('/users', dependencies=[Depends(require_admin)])
async def list_users():
users = []
async for u in users_col.find({}, {'password_hash': 0}):
users.append(obj_to_dict(u))
return users