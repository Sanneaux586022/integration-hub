from pydantic import BaseModel, EmailStr
from datetime import datetime

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
        