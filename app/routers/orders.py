# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.db import orders_collection, cart_collection, products_collection
from app.auth import get_current_user
from app.utils import obj_to_dict

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/create")
async def create_order(user: dict = Depends(get_current_user)):
    cart = cart_collection.find_one({"user_id": user["_id"]})

    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            total += product.get("price", 0) * item["quantity"]

    order_data = {
        "user_id": user["_id"],
        "items": cart["items"],
        "total": total,
        "status": "pending"
    }

    result = orders_collection.insert_one(order_data)

    cart_collection.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": []}}
    )

    return {"message": "Order created", "order_id": str(result.inserted_id)}

@router.get("/")
async def get_user_orders(user: dict = Depends(get_current_user)):
    orders = orders_collection.find({"user_id": user["_id"]})
    return [obj_to_dict(order) for order in orders]

@router.get("/{order_id}")
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    order = orders_collection.find_one({
        "_id": ObjectId(order_id),
        "user_id": user["_id"]
    })

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return obj_to_dict(order)
