from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from app.auth import require_admin
from database import products_col, orders_col, users_col
from models import ProductIn
from utils import obj_to_dict

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# -----------------------------------
# UPDATE PRODUCT
# -----------------------------------
@router.put("/products/{product_id}", dependencies=[Depends(require_admin)])
async def update_product(product_id: str, product: ProductIn):

    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product id")

    res = await products_col.update_one(
        {"_id": oid},
        {"$set": product.dict()}
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    updated = await products_col.find_one({"_id": oid})
    return obj_to_dict(updated)


# -----------------------------------
# DELETE PRODUCT
# -----------------------------------
@router.delete("/products/{product_id}", dependencies=[Depends(require_admin)])
async def delete_product(product_id: str):

    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product id")

    res = await products_col.delete_one({"_id": oid})

    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"detail": "Product deleted"}


# -----------------------------------
# LIST ALL ORDERS
# -----------------------------------
@router.get("/orders", dependencies=[Depends(require_admin)])
async def list_orders():

    orders = []
    async for o in orders_col.find():
        orders.append(obj_to_dict(o))

    return orders


# -----------------------------------
# UPDATE ORDER STATUS
# -----------------------------------
@router.put("/orders/{order_id}/status", dependencies=[Depends(require_admin)])
async def update_order_status(order_id: str, status: str):

    try:
        oid = ObjectId(order_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid order id")

    res = await orders_col.update_one(
        {"_id": oid},
        {"$set": {"status": status}}
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated = await orders_col.find_one({"_id": oid})
    return obj_to_dict(updated)


# -----------------------------------
# LIST ALL USERS (hides password hash)
# -----------------------------------
@router.get("/users", dependencies=[Depends(require_admin)])
async def list_users():

    users = []
    async for u in users_col.find({}, {"password_hash": 0}):
        users.append(obj_to_dict(u))

    return users
