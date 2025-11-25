from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.schemas.order import OrderCreateModel
from app.dependencies import get_current_user, admin_only
from database import orders_col, products_col

router = APIRouter()


@router.post("/")
def create_order(order: OrderCreateModel, user=Depends(get_current_user)):
    total_price = 0
    order_items = []

    for item in order.items:
        prod = products_col.find_one({"_id": ObjectId(item.product_id)})
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if prod["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {prod['name']}")
        total_price += prod["price"] * item.quantity
        order_items.append({"product_id": item.product_id, "quantity": item.quantity})
        products_col.update_one({"_id": ObjectId(item.product_id)}, {"$inc": {"stock": -item.quantity}})

    order_doc = {"user_id": user["_id"], "products": order_items, "total_price": total_price, "status": "pending"}
    result = orders_col.insert_one(order_doc)
    return {"msg": "Order created", "id": str(result.inserted_id)}
