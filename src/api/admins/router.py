from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.admins.schemas import (
    AdminOut,
    AdminCreateIn,
    AdminSetSuperIn,
)
from src.api.admins.services import AdminService
from src.core.infra.exceptions import NotFound, Conflict
from src.guards import require_admin, require_super_admin

router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    route_class=DishkaRoute,
)

# ----- READ -----

@router.get(
    "",
    response_model=list[AdminOut],
    dependencies=[Depends(require_admin)],
)
async def list_admins(service: FromDishka[AdminService]) -> list[AdminOut]:
    admins = await service.list_admins()
    return [AdminOut.model_validate(a) for a in admins]


@router.get(
    "/{user_id}",
    response_model=AdminOut,
    dependencies=[Depends(require_admin)],
)
async def get_admin(user_id: int, service: FromDishka[AdminService]) -> AdminOut:
    try:
        admin = await service.get_by_user_id(user_id)
        return AdminOut.model_validate(admin)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ----- (только супер-админ) -----

@router.post(
    "",
    response_model=AdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_super_admin)],
)
async def add_admin(
    data: AdminCreateIn,
    service: FromDishka[AdminService],
) -> AdminOut:
    try:
        admin = await service.add_admin(data)
        return AdminOut.model_validate(admin)
    except NotFound as e:
        # пользователь не найден
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Conflict as e:
        # уже является админом
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch(
    "/{user_id}/super",
    response_model=AdminOut,
    dependencies=[Depends(require_super_admin)],
)
async def set_super_flag(
    user_id: int,
    body: AdminSetSuperIn,
    service: FromDishka[AdminService],
) -> AdminOut:
    try:
        admin = await service.set_super_admin(user_id=user_id, value=body.super_admin)
        return AdminOut.model_validate(admin)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_super_admin)],
)
async def remove_admin(
    user_id: int,
    service: FromDishka[AdminService],
) -> None:
    await service.remove_admin(user_id)
    return
