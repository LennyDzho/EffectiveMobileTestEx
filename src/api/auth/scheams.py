import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator

class RegisterIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=100, description="Имя")
    last_name: str = Field(min_length=1, max_length=100, description="Фамилия")
    middle_name: Optional[str] = Field(default=None, max_length=100, description="Отчество")
    email: EmailStr = Field(description="E-mail пользователя")
    password: str = Field(min_length=6, description="Пароль пользователя")
    password_confirm: str = Field(min_length=6, description="Повтор пароля")

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterIn":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class LoginIn(BaseModel):
    email: EmailStr = Field(description="E-mail пользователя")
    password: str = Field(min_length=1, description="Пароль")


class LogoutIn(BaseModel):
    reason: Optional[str] = Field(default=None, description="Причина выхода")


class UserData(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RegisterResponse(BaseModel):
    user: UserData


class LoginResponse(BaseModel):
    ok: bool = True


class LogoutResponse(BaseModel):
    ok: bool = True


class MeResponse(BaseModel):
    user: UserData