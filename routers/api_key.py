from fastapi import APIRouter, Depends

from auth.security import get_api_key


router = APIRouter()


@router.get("/")
def validate_key(_: str = Depends(get_api_key)):
    return {"message": "API Key is valid"}
