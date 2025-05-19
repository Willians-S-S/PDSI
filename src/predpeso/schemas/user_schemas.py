from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from predpeso.schemas.farm_schemas import FarmResponse

class UserRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
    cpf: str | None = None
    profile_picture: str | None = None
    role: str | None = None

class UserResponse(BaseModel):
    id: str | None = None
    name: str | None = None
    username: str | None = None
    email: str | None = None
    cpf: str | None = None
    profile_picture: str | None = None
    role: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    farms: Optional[List[FarmResponse]] = []


class UserUpdate(BaseModel):
    name: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
    cpf: str | None = None
    profile_picture: str | None = None
    role: str | None = None