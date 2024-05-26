# FastAPI Authentication Sidecar
## Overview
This project aims to reduce authentication code across microservices by abstracting the logic (such as verifying API keys or creating event logs) into an easily configured reverse proxy. I chose to build this in Python (instead of something like Istio or Envoy) and Firebase because that's all I know how to use.

The sidecar parses special route requirements by either looking for a `config.json` file (see below) or parsing an OpenAPI schema and looking for routes and special flags. Currently it only looks for `require_api_key`.

If you don't want to use Firebase, you can rewrite the `auth.py` logic and change the `# ---Auth logic---` block and `# ---Route Logic---` block in `main.py`.
## Dependencies
- Python 3.10
- Google Firebase
- Cloud Firestore
## Setup
1. If using Firebase/Firestore, create a `.env` file in the `app` directory and add your Firebase service account JSON contents and config to the `SERVICE_ACCOUNT` and `CONFIG` variables, respectively.
2. Create a `config.json` file (see below)
3. Run `dev.sh`
## Configuration
The sidecar looks for a `config.json` file to extract a port for the sidecar and service. 

You can pass an optional `include_route_configs` boolean and then your own routes. An example of a `config.json` looks like the following:

```
{
    "forward_port": 8004,
    "sidecar_port": 9004,
    "include_route_configs": true,
    "route_configs":{
        "prefix": "/api/v1/endpoint",
        "routes": {
            "/": {
                "methods": ["GET"],
                "require_api_key": false
            },
            "/get": {
                "methods": ["GET"],
                "require_api_key": true
            },
            "/create": {
                "methods": ["POST"],
                "require_api_key": true
            },
            "/update": {
                "methods": ["PUT"],
                "require_api_key": true
            },
            "/delete": {
                "methods": ["DELETE"],
                "require_api_key": true
            }
        }
    }
}
```
If the `include_route_configs` value is `false`, then the sidecar will attempt to look for an OpenAPI schema to parse routes and special attributes. To add these attributes, simple add the `openapi_extra` argument to your route definitions and reference those in a helper.
## Todo
1. Learn to code