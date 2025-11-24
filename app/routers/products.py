from fastapi import APIRouter, HTTPException
from typing import List
from app.db import products_col
from app.utils import obj_to_dict
from app.models import ProductIn, ProductOut


router = APIRouter(prefix='/products', tags=['products'])


@router.get('', response_model=List[ProductOut])
async def list_products():
products = []
async for doc in products_col.find():
products.append(obj_to_dict(doc))
return products


@router.get('/{product_id}', response_model=ProductOut)
async def get_product(product_id: str):
import bson
try:
doc = await products_col.find_one({'_id': bson.ObjectId(product_id)})
except Exception:
doc = None
if not doc:
raise HTTPException(status_code=404, detail='Product not found')
return obj_to_dict(doc)