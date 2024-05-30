import httpx
from httpx import AsyncClient
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
import json

from auth import verify_api_key
from helpers import fetch_openapi_schema, parse_require_api_key

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('config.json', 'r') as file:
    config = json.load(file)

FORWARD_PORT = config.get('forward_port')
SIDECAR_PORT = config.get('sidecar_port')
INCLUDE_ROUTE_CONFIGS = config.get('include_route_configs')
ROUTE_CONFIGS = config.get('route_configs', {}).get('routes', {})
PREFIX = ''

BASE_URL = f"http://127.0.0.1:{FORWARD_PORT}"


HTTP_SERVER = AsyncClient(base_url=BASE_URL)

async def reverse_proxy(request: Request):
    
    # ---Auth logic---
    route_path = request.url.path
    route_config = ROUTES.get(route_path, {})
    require_api_key = route_config.get("require_api_key", True)

    if require_api_key:
        try:
            request = await verify_api_key(request)
        except Exception as err:
            return Response(str(err), status_code=401)
    # ---Auth logic---
    
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

# ---Route Logic---
# Determine route configurations
if INCLUDE_ROUTE_CONFIGS:
    ROUTES = ROUTE_CONFIGS
    PREFIX = config.get('route_configs', {}).get('prefix', '')
else:
    # Fetch and parse the OpenAPI schema
    openapi_url = f"{BASE_URL}/openapi.json"
    openapi_schema = fetch_openapi_schema(openapi_url)
    ROUTES = parse_require_api_key(openapi_schema)

for route, settings in ROUTES.items():
    for method in settings.get("methods", []):
        app.add_api_route(f"{PREFIX}{route}", reverse_proxy, methods=[method])
# ---Route Logic---
