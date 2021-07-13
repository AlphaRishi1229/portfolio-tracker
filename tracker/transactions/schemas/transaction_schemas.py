from pydantic import BaseModel, validator

from utils.constants import VALID_TRANSACTIONS


class BaseResponse(BaseModel):
    """Base Response for adding updating data."""
    success: bool = False
    message: str = ""
    ref_id: str = ""


class TradeTransaction(BaseModel):
    """Base Transaction Schema required for adding a transaction."""
    security_id: int = 0
    transaction_type: str = ""
    transaction_amount: float = 0.0
    quantity: int = 0

    @validator("transaction_type")
    def is_valid_transaction(cls, transaction):
        if transaction not in VALID_TRANSACTIONS:
            raise ValueError("transaction_type can only be BUY or SELL.")
        return transaction

    @validator("transaction_amount")
    def is_valid_amount(cls, amount):
        if amount <= 0:
            raise ValueError("transaction_amount can not be less than or equal to 0.")
        return amount

    @validator("quantity")
    def is_valid_quantity(cls, quantity):
        if quantity <= 0:
            raise ValueError("quantity can not be less than or equal to 0.")
        return quantity


class UpdateTrade(TradeTransaction):
    """Trade updating schema."""
    updating_portfolio_id: int = 0

    @validator("updating_portfolio_id")
    def is_valid_portfolio_id(cls, updating_portfolio_id):
        if updating_portfolio_id == 0:
            raise ValueError("Invalid portfolio id.")
        return updating_portfolio_id


class DeleteTrade(BaseModel):
    """Trade deleting schema."""
    portfolio_id: int = 0

    @validator("portfolio_id")
    def is_valid_delete_portfolio_id(cls, portfolio_id):
        if portfolio_id == 0:
            raise ValueError("Invalid portfolio id.")
        return portfolio_id
