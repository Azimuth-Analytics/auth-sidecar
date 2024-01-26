import json
import csv
import inspect
import time

from functools import wraps
from io import StringIO

from fastapi import Form

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
        api_key = args[1]
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time} seconds')
        return result
    return timeit_wrapper
        