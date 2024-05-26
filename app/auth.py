import json
import os
from fastapi import Request, Response
from functools import wraps
from firebase_admin import firestore, credentials, initialize_app

from dotenv import load_dotenv
load_dotenv()

# Load Firebase credentials
firebase_credentials = json.loads(os.getenv('SERVICE_ACCOUNT'), strict=False)
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)


async def verify_api_key(request: Request):
    api_key: str = None
    try:
        api_key = request.headers["Authorization"].split(' ')[1]
    except Exception as err:
        print(err)
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
            print(err)
            raise Exception('Invalid or missing API key')
        
def get_uid(api_key):
    try:
        db = firestore.client()
        user_ref = db.collection(u'users').where(u'api_key', u'==', api_key).get()
        uid = (user_ref[0].id)
        return uid
    except Exception as error:
        print(error)
        return Response('Unable to verify user.', status_code=500)