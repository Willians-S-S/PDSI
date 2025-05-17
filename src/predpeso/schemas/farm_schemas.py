from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# from predpeso.schemas.animal_schemas import AnimalResponse

class FarmRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    animal_quantity: int | None = None
    user_id: str | None = None

class FarmResponse(BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    animal_quantity: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    user_id: str | None = None
    # animals: list[AnimalResponse] | None = None 

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    animal_quantity: Optional[int] = None