from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.guards import require_user
from src.api.users.schemas import UpdateProfileDTO, UserOut
from src.api.users.services import UserService, NotFound, Conflict, Forbidden
from src.database.models import User
from src.api.auth.services import COOKIE_NAME

router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,  # как и в auth
)

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(require_user)) -> UserOut:
    return UserOut.model_validate(current_user)

@router.patch("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_me(
    data: UpdateProfileDTO,
    user_service: FromDishka[UserService],
    current_user: User = Depends(require_user),
) -> UserOut:
    try:
        user = await user_service.update_profile(current_user.id, data)
        return UserOut.model_validate(user)
    except Conflict as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    response: Response,
    user_service: FromDishka[UserService],
    current_user: User = Depends(require_user),
) -> None:
    await user_service.soft_delete(current_user.id)
    response.delete_cookie(COOKIE_NAME, path="/")
    return
