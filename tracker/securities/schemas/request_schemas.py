from pydantic import BaseModel


class UserBase(BaseModel):
    """Basic Input Validation while displaying user details."""
    name: str = ""
    userid: str = ""
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = ""
