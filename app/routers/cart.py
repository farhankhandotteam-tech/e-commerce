# app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.db import cart_collection, products_collection
from app.auth import get_current_user
from app.utils import obj_to_dict

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/")
async def get_cart(user: dict = Depends(get_current_user)):
    cart = cart_collection.find_one({"user_id": user["_id"]})
    if not cart:
        return {"items": []}
    return obj_to_dict(cart)

@router.post("/add/{product_id}")
async def add_to_cart(product_id: str, quantity: int = 1, user: dict = Depends(get_current_user)):
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = cart_collection.find_one({"user_id": user["_id"]})

    if not cart:
        cart_collection.insert_one({
            "user_id": user["_id"],
            "items": [{"product_id": product_id, "quantity": quantity}]
        })
    else:
        updated = False
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                updated = True

        if not updated:
            cart["items"].append({"product_id": product_id, "quantity": quantity})

        cart_collection.update_one(
            {"_id": cart["_id"]},
            {"$set": {"items": cart["items"]}}
        )

    return {"message": "Item added to cart"}

@router.delete("/remove/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    cart = cart_collection.find_one({"user_id": user["_id"]})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    new_items = [item for item in cart["items"] if item["product_id"] != product_id]

    cart_collection.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": new_items}}
    )

    return {"message": "Item removed from cart"}
