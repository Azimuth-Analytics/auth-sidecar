from pydantic import BaseModel
from typing import Any

from helpers import parse_contents, as_form, convert_vals

from fastapi import APIRouter, Request, Depends
router = APIRouter()

from middleware import verify_api_key

@as_form
class NgramQuery(BaseModel):
    data: Any
    key: str | None = None
    preprocess: bool | None = False
    preprocessor_type: str | None = "stem"
    remove_stopwords: bool | None = False
    ngram_min: int | None = 1
    ngram_max: int | None = 3
    remove_substrings: bool | None = False
    sort_by: str | None = "length"
    sort_by_reverse: bool | None = False
    extra_stopwords: list | None = []
    score: bool | None = False

@router.post("/api/v1/text/ngrams")
@verify_api_key
async def ngrams(request: Request, form: NgramQuery = Depends(NgramQuery.as_form)):
    api_key = request.headers["Authorization"].split(' ')[1]
    data = convert_vals(form.dict())
    
