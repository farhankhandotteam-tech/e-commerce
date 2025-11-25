from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
from database import products_col
from models.product import Product
from dependencies import admin_required
import os, shutil
from config import IMAGE_DIR

router = APIRouter()

os.makedirs(IMAGE_DIR, exist_ok=True)

@router.get("/")
def get_products():
    return [{"_id": str(p["_id"]), **p} for p in products_col.find()]

@router.get("/{id}")
def get_product(id: str):
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(404, "Product not found")
    product["_id"] = str(product["_id"])
    return product

@router.post("/")
def create_product(product: Product, image: UploadFile = File(...), user=Depends(admin_required)):
    image_path = os.path.join(IMAGE_DIR, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    product_dict = product.dict()
    product_dict["image_url"] = f"/images/{image.filename}"
    result = products_col.insert_one(product_dict)
    return {"msg": "Product created", "id": str(result.inserted_id), "image_url": product_dict["image_url"]}

@router.put("/{id}")
def update_product(id: str, product: Product, image: Optional[UploadFile] = None, user=Depends(admin_required)):
    update_data = product.dict()
    if image:
        image_path = os.path.join(IMAGE_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        update_data["image_url"] = f"/images/{image.filename}"
    result = products_col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, "Product not found")
    return {"msg": "Product updated"}

@router.delete("/{id}")
def delete_product(id: str, user=Depends(admin_required)):
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(404, "Product not found")
    if "image_url" in product:
        img_path = product["image_url"].replace("/images/", IMAGE_DIR + "/")
        if os.path.exists(img_path):
            os.remove(img_path)
    products_col.delete_one({"_id": ObjectId(id)})
    return {"msg": "Product deleted"}
