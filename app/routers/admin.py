from fastapi import APIRouter, Depends, HTTPException, status
from database import db
from dependencies import get_current_user

router = APIRouter()

# Check if current user is admin
def check_admin(current_user):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

# Get all users (admin only)
@router.get("/users")
async def get_all_users(current_user=Depends(get_current_user)):
    check_admin(current_user)
    users = list(db.users.find({}, {"password": 0}))
    return users


# Delete any user (admin only)
@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    check_admin(current_user)
    result = db.users.delete_one({"_id": user_id})
    return {"message": "User deleted" if result.deleted_count else "User not found"}


# Admin can add new product
@router.post("/products")
async def admin_add_product(product: dict, current_user=Depends(get_current_user)):
    check_admin(current_user)
    db.products.insert_one(product)
    return {"message": "Product added successfully"}


# Admin can delete product
@router.delete("/products/{product_id}")
async def admin_delete_product(product_id: str, current_user=Depends(get_current_user)):
    check_admin(current_user)
    db.products.delete_one({"_id": product_id})
    return {"message": "Product deleted"}
