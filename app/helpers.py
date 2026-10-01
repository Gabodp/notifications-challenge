from fastapi import HTTPException, status

from app.enums import Entity


def entity_not_found_exception(entity: Entity):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity.value} not found"
    )


def action_not_authorized(entity: Entity):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Not authorized to edit/delete this {entity.value}",
    )


def entity_already_exists_exception(entity: Entity):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=f"{entity.value} already exists"
    )
