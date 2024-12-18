from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

class Base(BaseModel):
    created_at: datetime
    updated_at: datetime

class UserBase(Base):
    id: int
    name: str
    surname: str
    username: str
    email: EmailStr
    password: str
    
    

class UserGet(UserBase):
    pass
    

# User Create DTO
class UserCreate(BaseModel):

    name: str
    surname: str
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = None

# User Update DTO
class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
# User delete DTO
class UserDelete(BaseModel):
    id: int