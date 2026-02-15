from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email : EmailStr
    username : str

class UserCreate(UserBase):
    password : str

class UserOut(UserBase):
    id : int
    createAt : datetime
    modifyAt : datetime

    model_config = {
        "from_attributes" : True
    }

class UserLogin(BaseModel):
    email: EmailStr
    plain_password : str


class Token(BaseModel):
    access_token: str
    token_type : str

class TokenData(BaseModel):
    email: Optional[str] = None