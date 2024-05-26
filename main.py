import httpx
from httpx import AsyncClient
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware

# Builtins
import json
import os

# Firebase Admin
import firebase_admin
from firebase_admin import credentials

# Dotenv
from dotenv import load_dotenv
load_dotenv()

from auth import verify_api_key

# Load JSON variables
with open('config.json', 'r') as file:
    config = json.load(file)

FORWARD_PORT = config.get('forward_port')
SIDECAR_PORT = config.get('sidecar_port')
METHODS = config.get('methods')
ROUTES = config.get('routes')

# Load creds
firebase_credentials = json.loads(os.getenv('SERVICE_ACCOUNT'), strict=False)
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTTP_SERVER = AsyncClient(base_url=f"http://localhost:{FORWARD_PORT}")

async def _reverse_proxy(request: Request):
    route_config = ROUTES.get(request.url.path, {})
    require_api_key = route_config.get("require_api_key", True)
    
    if require_api_key:
        try:
            request = await verify_api_key(request)
        except Exception as err:
            return Response(str(err), status_code=401)
    
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    rp_req = HTTP_SERVER.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    rp_resp = await HTTP_SERVER.send(rp_req, stream=True)
    
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )

# Dynamically add routes based on config
for route, settings in ROUTES.items():
    for method in settings.get("methods", []):
        app.add_api_route(route, _reverse_proxy, methods=[method])