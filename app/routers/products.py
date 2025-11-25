from fastapi import APIRouter, HTTPException, Depends
from app.database import products_collection
from app.dependencies import verify_token, admin_only

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------- CREATE PRODUCT (ADMIN ONLY) ----------------
@router.post("/create")
def create_product(data: dict, admin=Depends(admin_only)):

    products_collection.insert_one(data)
    return {"message": "Product created", "product": data}


# ---------------- UPDATE PRODUCT (ADMIN ONLY) ----------------
@router.put("/update/{product_id}")
def update_product(product_id: str, data: dict, admin=Depends(admin_only)):

    result = products_collection.update_one({"_id": product_id}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated"}


# ---------------- DELETE PRODUCT (ADMIN ONLY) ----------------
@router.delete("/delete/{product_id}")
def delete_product(product_id: str, admin=Depends(admin_only)):

    result = products_collection.delete_one({"_id": product_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted"}


# ---------------- GET ALL PRODUCTS (PUBLIC) ----------------
@router.get("/")
def get_all_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return products


# ---------------- GET ONE PRODUCT (PUBLIC) ----------------
@router.get("/{product_id}")
def get_product(product_id: str):
    product = products_collection.find_one({"_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
