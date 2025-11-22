from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_current_user, admin_required
from ..db import db
from bson import ObjectId
from datetime import datetime
from ..models import OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", dependencies=[Depends(get_current_user)])
async def place_order(payload: OrderCreate, current_user=Depends(get_current_user)):
    # If items not provided, use cart
    items = []
    if payload.items:
        items = [item.dict() for item in payload.items]
    else:
        cart = await db.carts.find_one({"user_id": current_user["_id"]})
        if not cart or not cart.get("items"):
            raise HTTPException(400, "Cart is empty")
        # convert cart items to order items
        for it in cart["items"]:
            prod = await db.products.find_one({"_id": ObjectId(it["product_id"])})
            if not prod:
                raise HTTPException(400, f"Product {it['product_id']} not found")
            items.append({"product_id": it["product_id"], "qty": it["qty"], "price": prod["price"]})

    # check stock & decrement atomically
    for it in items:
        pid = ObjectId(it["product_id"])
        qty = int(it["qty"])
        res = await db.products.update_one({"_id": pid, "stock": {"$gte": qty}}, {"$inc": {"stock": -qty}})
        if res.modified_count == 0:
            raise HTTPException(400, f"Not enough stock for product {it['product_id']}")

    total = sum(it["qty"] * it["price"] for it in items)
    order_doc = {
        "user_id": current_user["_id"],
        "items": items,
        "total": total,
        "address": payload.address,
        "payment_method": payload.payment_method,
        "payment_status": "pending" if payload.payment_method != "cod" else "pending",
        "order_status": "created",
        "created_at": datetime.utcnow(),
    }
    res = await db.orders.insert_one(order_doc)
    # clear cart
    await db.carts.delete_one({"user_id": current_user["_id"]})
    return {"message": "Order placed", "order_id": str(res.inserted_id)}

@router.get("/", dependencies=[Depends(get_current_user)])
async def list_orders(current_user=Depends(get_current_user)):
    # user orders
    cursor = db.orders.find({"user_id": current_user["_id"]})
    out = []
    async for o in cursor:
        o["_id"] = str(o["_id"])
        out.append(o)
    return out

# admin endpoints
@router.get("/admin/all", dependencies=[Depends(admin_required)])
async def admin_list_all_orders():
    out = []
    async for o in db.orders.find().sort("created_at", -1):
        o["_id"] = str(o["_id"])
        out.append(o)
    return out

@router.patch("/admin/{order_id}/status", dependencies=[Depends(admin_required)])
async def admin_update_status(order_id: str, payload: dict):
    status = payload.get("status")
    if not status:
        raise HTTPException(400, "status required")
    res = await db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"order_status": status}})
    if res.matched_count == 0:
        raise HTTPException(404, "Order not found")
    return {"message": "Order status updated"}
