from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, Response

from src.api.auth.scheams import (
    RegisterIn, RegisterResponse,
    LoginIn, LoginResponse,
    LogoutResponse,
    MeResponse, UserData,
)
from src.api.auth.services import AuthService, COOKIE_NAME, DEFAULT_SESSION_TTL

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute,  # чтобы AuthService инжектился через Dishka
)


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(data: RegisterIn, service: FromDishka[AuthService]):
    user = await service.register(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
    )
    return RegisterResponse(user=UserData.model_validate(user))


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginIn,
    response: Response,
    service: FromDishka[AuthService],
):
    sid = await service.login(email=data.email, password=data.password)

    # Ставим cookie сессии
    response.set_cookie(
        key=COOKIE_NAME,
        value=sid,                 # только SID; данные сессии лежат в Redis
        httponly=True,
        secure=True,               # в dev можно сделать False, если тестируешь без HTTPS
        samesite="lax",
        max_age=DEFAULT_SESSION_TTL,
        path="/",
    )
    return LoginResponse()


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
):
    sid = request.cookies.get(COOKIE_NAME)
    await service.logout_by_sid(sid)

    # Чистим cookie у клиента
    response.delete_cookie(COOKIE_NAME, path="/")
    return LogoutResponse()


@router.get("/me", response_model=MeResponse)
async def me(
    request: Request,
    service: FromDishka[AuthService],
):
    sid = request.cookies.get(COOKIE_NAME)
    user = await service.get_current_user(sid)
    return MeResponse(user=UserData.model_validate(user))
