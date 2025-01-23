from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class UserResponse(UserBase):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
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
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
    class Config:
        orm_mode = True