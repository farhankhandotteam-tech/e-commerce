from fastapi import HTTPException
from bson import ObjectId
from app.utils import obj_to_dict
from app.db import products_col

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):

    try:
        doc = await products_col.find_one({"_id": ObjectId(product_id)})
    except Exception:
        doc = None

    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    return obj_to_dict(doc)
