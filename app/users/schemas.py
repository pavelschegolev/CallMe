from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserME(BaseModel):
    id: int
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes  = True
