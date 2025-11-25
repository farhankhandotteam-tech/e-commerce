from fastapi import APIRouter, Depends, HTTPException
from models.order import Order
from database import orders_col, products_col
from dependencies import get_current_user, admin_required
from bson import ObjectId

router = APIRouter()

@router.post("/")
def create_order(order: Order, user=Depends(get_current_user)):
    total_price = 0
    order_items = []
    for item in order.products:
        prod = products_col.find_one({"_id": ObjectId(item.product_id)})
        if not prod:
            raise HTTPException(404, f"Product {item.product_id} not found")
        if prod["stock"] < item.quantity:
            raise HTTPException(400, f"Not enough stock for {prod['name']}")
        total_price += prod["price"] * item.quantity
        order_items.append({"product_id": item.product_id, "quantity": item.quantity})
        products_col.update_one({"_id": ObjectId(item.product_id)}, {"$inc": {"stock": -item.quantity}})
    order_doc = {"user_id": user["_id"], "products": order_items, "total_price": total_price, "status": "pending"}
    result = orders_col.insert_one(order_doc)
    return {"msg": "Order created", "id": str(result.inserted_id)}

@router.get("/")
def get_orders(user=Depends(get_current_user)):
    if user["role"] == "admin":
        orders = list(orders_col.find())
    else:
        orders = list(orders_col.find({"user_id": user["_id"]}))
    for o in orders:
        o["_id"] = str(o["_id"])
    return orders

@router.get("/{id}")
def get_order(id: str, user=Depends(get_current_user)):
    order = orders_col.find_one({"_id": ObjectId(id)})
    if not order:
        raise HTTPException(404, "Order not found")
    if user["role"] != "admin" and order["user_id"] != user["_id"]:
        raise HTTPException(403, "Access denied")
    order["_id"] = str(order["_id"])
    return order

@router.put("/{id}/status")
def update_order_status(id: str, status: str, user=Depends(admin_required)):
    result = orders_col.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(404, "Order not found")
    return {"msg": "Order status updated"}
