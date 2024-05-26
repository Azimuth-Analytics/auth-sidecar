from fastapi import Request, Response
from functools import wraps
from firebase_admin import firestore

# def verify_api_key(func):
#     @wraps(func)
#     async def wrapper(*args, request: Request, **kwargs):
#         api_key = request.headers["Authorization"].split(' ')[1]
#         if not api_key:
#             return Response("No API key found.", status_code=401)
#         else:
#             try:
#                 db = firestore.client()
#                 user_ref = db.collection(u'users').where(u'api_key', u'==', api_key).get()
#                 user_data = user_ref[0].to_dict()
#                 if user_data:
#                     return await func(*args, request, **kwargs)
#             except Exception as err:
#                 print(err)
#                 return Response("Invalid or missing API key.", status_code=401)      
#     return wrapper

async def verify_api_key(request: Request):
    api_key: str = None
    try:
        api_key = request.headers["Authorization"].split(' ')[1]
    except Exception as err:
        raise Exception('Missing Authorization header')
    if not api_key:
        raise Exception('API key not found')
    else:
        try:
            db = firestore.client()
            user_ref = db.collection(u'users').where(u'api_key', u'==', api_key).get()
            user_data = user_ref[0].to_dict()
            if user_data:
                return request
        except Exception as err:
            raise Exception('Invalid or missing API key')