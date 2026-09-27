
from http.client import HTTPException
from fastapi import status
from enums import Entity


def entity_not_found_exception(entity: Entity): 
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity.value} not found"
    )
