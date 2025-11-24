

from typing import Any

def obj_to_dict(doc: Any) -> dict:
    if doc is None:
        return None

    doc = dict(doc)

    _id = doc.get("_id")

    if _id is not None:
        doc["id"] = str(_id)
        del doc["_id"]   

    return doc  
