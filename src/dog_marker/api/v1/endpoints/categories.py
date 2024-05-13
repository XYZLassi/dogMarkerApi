from typing import Annotated

from fastapi import APIRouter, Depends

from .dependecies import get_service
from ..schemas import CategorySchema
from ..services import CategoryService

router = APIRouter()


@router.get("/", response_model=list[CategorySchema], operation_id="get_all_categories")
async def get_all_categories(service: Annotated[CategoryService, Depends(get_service(CategoryService))]):
    return service.all()
