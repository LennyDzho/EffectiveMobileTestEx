from pydantic import BaseModel, Field, ConfigDict


class AdminOut(BaseModel):
    id: int
    user_id: int
    super_admin: bool

    model_config = ConfigDict(from_attributes=True)


class AdminCreateIn(BaseModel):
    user_id: int = Field(gt=0, description="ID пользователя, которому выдаём права")
    super_admin: bool = Field(default=False, description="Сделать сразу супер-админом")


class AdminSetSuperIn(BaseModel):
    super_admin: bool = Field(description="Новое значение признака супер-админа")
