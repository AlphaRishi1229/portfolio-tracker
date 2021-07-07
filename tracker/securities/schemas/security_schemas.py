import datetime

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base Response for adding updating data."""
    success: bool = False
    message: str = ""


class SecurityBase(BaseModel):
    """Basic Input Validation while displaying security details."""
    name: str = ""
    ticker_symbol: str = ""
    current_price: float = 0.0


class SecurityCreate(SecurityBase):
    """Schema for creating a security."""
    is_active: bool = True


class SecurityUpdate(BaseModel):
    """Schema for updating the price of a security."""
    id: int = 0
    current_price: float = 0.0


class SecurityResponse(BaseModel):
    """Response Schema for all the data related to security."""
    id: int = 0
    name: str = ""
    ticker_symbol: str = ""
    current_price: float = 0.0
    updated_on: datetime.datetime = ""
