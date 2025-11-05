from pydantic import BaseModel, EmailStr
from typing import List

class Organization(BaseModel):
    name: str

class QuayConfig(BaseModel):
    organizations: List[Organization]