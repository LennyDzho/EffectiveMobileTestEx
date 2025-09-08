from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UpdateProfileDTO(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str]  = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)

    @field_validator("email", "first_name", "last_name", "middle_name", mode="before")
    @classmethod
    def empty_to_none_and_strip(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: str | None
    is_active: bool