from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserRead(UserBase):  # Add this schema
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class LoginSchema(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None

    class Config:
        orm_mode = True