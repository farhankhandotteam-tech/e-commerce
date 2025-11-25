from fastapi import APIRouter, Depends, HTTPException
from database import db
from auth import get_current_user
from app.database import orders_col, products_col
router = APIRouter()

# Add product to cart
@router.post("/add")
async def add_to_cart(product_id: str, qty: int = 1, current_user=Depends(get_current_user)):
    user_id = current_user["_id"]

    cart_item = db.cart.find_one({"user_id": user_id, "product_id": product_id})

    if cart_item:
        db.cart.update_one(
            {"_id": cart_item["_id"]},
            {"$inc": {"qty": qty}}
        )
    else:
        db.cart.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "qty": qty
        })
    
    return {"message": "Added to cart"}

# Get cart
@router.get("/")
async def get_cart(current_user=Depends(get_current_user)):
    user_id = current_user["_id"]
    items = list(db.cart.find({"user_id": user_id}))
    return items

# Remove product
@router.delete("/{product_id}")
async def remove_from_cart(product_id: str, current_user=Depends(get_current_user)):
    user_id = current_user["_id"]
    db.cart.delete_one({"user_id": user_id, "product_id": product_id})
    return {"message": "Removed from cart"}

# Clear cart
@router.delete("/")
async def clear_cart(current_user=Depends(get_current_user)):
    user_id = current_user["_id"]
    db.cart.delete_many({"user_id": user_id})
    return {"message": "Cart cleared"}
