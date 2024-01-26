from functools import wraps
from fastapi import Request, Response, Form
from firebase_admin import firestore

def verify_api_key(func):
    @wraps(func)
    async def wrapper(*args, request: Request, form: Form, **kwargs):
        api_key = request.headers["Authorization"].split(' ')[1]
        if not api_key:
            return Response("No API key found.", status_code=401)
        else:
            try:
                db = firestore.client()
                user_ref = db.collection(u'users').where(u'api_key', u'==', api_key).get()
                user_data = user_ref[0].to_dict()
                if user_data:
                    return await func(*args, request, form, **kwargs)
            except Exception as err:
                print(err)
                return Response("Invalid or missing API key.", status_code=401)      
    return wrapper