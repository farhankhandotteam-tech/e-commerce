from fastapi import APIRouter, Depends, HTTPException
from deps import get_current_user
from db import db
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", dependencies=[Depends(get_current_user)])
async def get_cart(current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_id": current_user["_id"]})
    if not cart:
        return {"user_id": current_user["_id"], "items": []}
    # populate product info for convenience
    items = []
    for it in cart.get("items", []):
        prod = await db.products.find_one({"_id": ObjectId(it["product_id"])})
        if prod:
            items.append({
                "product_id": it["product_id"],
                "title": prod.get("title"),
                "price": prod.get("price"),
                "qty": it.get("qty", 1)
            })
    return {"user_id": current_user["_id"], "items": items, "updated_at": cart.get("updated_at")}

@router.post("/add", dependencies=[Depends(get_current_user)])
async def add_to_cart(payload: dict, current_user=Depends(get_current_user)):
    # payload: {"product_id": "...", "qty": 1}
    pid = payload.get("product_id")
    qty = int(payload.get("qty", 1))
    if not pid:
        raise HTTPException(400, "product_id required")
    prod = await db.products.find_one({"_id": ObjectId(pid)})
    if not prod:
        raise HTTPException(404, "Product not found")
    # upsert cart
    res = await db.carts.update_one(
        {"user_id": current_user["_id"], "items.product_id": pid},
        {"$inc": {"items.$.qty": qty}, "$set": {"updated_at": datetime.utcnow()}}
    )
    if res.matched_count == 0:
        await db.carts.update_one(
            {"user_id": current_user["_id"]},
            {"$push": {"items": {"product_id": pid, "qty": qty}}, "$set": {"updated_at": datetime.utcnow()}},
            upsert=True
        )
    return {"message": "Added to cart"}

@router.patch("/update", dependencies=[Depends(get_current_user)])
async def update_cart(payload: dict, current_user=Depends(get_current_user)):
    pid = payload.get("product_id")
    qty = int(payload.get("qty", 1))
    if qty <= 0:
        # remove item
        await db.carts.update_one({"user_id": current_user["_id"]}, {"$pull": {"items": {"product_id": pid}}, "$set": {"updated_at": datetime.utcnow()}})
        return {"message": "Item removed"}
    res = await db.carts.update_one({"user_id": current_user["_id"], "items.product_id": pid}, {"$set": {"items.$.qty": qty, "updated_at": datetime.utcnow()}})
    if res.matched_count == 0:
        raise HTTPException(404, "Item not in cart")
    return {"message": "Cart updated"}

@router.delete("/clear", dependencies=[Depends(get_current_user)])
async def clear_cart(current_user=Depends(get_current_user)):
    await db.carts.delete_one({"user_id": current_user["_id"]})
    return {"message": "Cart cleared"}
