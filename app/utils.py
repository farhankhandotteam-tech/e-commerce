from bson import ObjectId


class PyObjectId(ObjectId):
 @classmethod
 def __get_validators__(cls):
  yield cls.validate


@classmethod
def validate(cls, v):
 if not ObjectId.is_valid(v):
  raise ValueError('Invalid objectid')
  return ObjectId(v)




def obj_to_dict(doc: dict) -> dict:
 if doc is None:
  return None
doc = dict(doc)
_id = doc.get('_id')
if _id is not None:
 doc['id'] = str(_id)
del doc['_id']
return doc