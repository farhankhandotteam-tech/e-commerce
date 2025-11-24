from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.db import products_col
from app.utils import ProductOut
import os
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)
@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):

    try:
        doc = await products_col.find_one({"_id": ObjectId(product_id)})
    except Exception:
        doc = None

    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    return obj_to_dict(doc)
UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=dict)
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None)
):
    image_url = None

    if image:
        image_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = image_path  # you can later replace with URL if uploading to cloud

    product = {
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url
    }

    result = await products_col.insert_one(product)
    product["id"] = str(result.inserted_id)
    return product