import json
import csv
import inspect
import time
import httpx

from functools import wraps
from io import StringIO

from fastapi import Request, Response, Form

from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import Type

def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField  # type: ignore

        new_parameters.append(
             inspect.Parameter(
                 model_field.alias,
                 inspect.Parameter.POSITIONAL_ONLY,
                 default=Form(...) if model_field.required else Form(model_field.default),
                 annotation=model_field.outer_type_,
             )
         )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'as_form', as_form_func)
    return cls

async def parse_contents(data):
    try:
        content_type = data.content_type
        if content_type == 'text/csv':
            contents = await data.read()
            buffer = StringIO(contents.decode('utf-8'))
            reader = csv.DictReader(buffer)
            return list(reader)
        elif content_type == 'application/json':
            contents = await data.read()
            contents_dict = json.loads(contents)
            return contents_dict
    except:
        return data
    
def convert_vals(object):
    keys = list(object.keys())
    for key in keys:
        if object[key] == 'null':
            object[key] = None
        elif object[key] == 'true':
            object[key] = True
        elif object[key] == 'false':
            object[key] = False
    return object

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        api_key = args[0]
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time} seconds')
        return result
    return timeit_wrapper

# Function to fetch and parse the OpenAPI schema from the target microservice
def fetch_openapi_schema(url):
    response = httpx.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch OpenAPI schema", status_code=response.status_code)

def parse_require_api_key(openapi_schema):
    routes_require_api_key = {}
    for path, methods in openapi_schema["paths"].items():
        for method, details in methods.items():
            if "require_api_key" in details:
                routes_require_api_key[path] = {
                    "methods": [method.upper()],
                    "require_api_key": details["require_api_key"]
                }
    return routes_require_api_key     