from typing import List

from fastapi import Depends, HTTPException

from tracker.transactions.helpers.transaction_db_helpers import (
    delete_last_transaction, get_all_trades,
    new_transaction, update_last_transaction, valid_transaction
)
from tracker.transactions.schemas.transaction_schemas import BaseResponse, DeleteTrade, TradeTransaction, UpdateTrade
from tracker.users.schemas.user_schemas import UserResponse
from tracker.users.handlers.user_handler import authorise_user
from utils.constants import UNPROCESSABLE_ENTITY


async def new_trade(transaction_data: TradeTransaction, user: UserResponse = Depends(authorise_user)) -> BaseResponse:
    success: bool = False
    message: str = "TRANSACTION_SUCCESSFUL"

    valid, message, existing_data = valid_transaction(transaction_data=transaction_data, user_data=UserResponse(**user))
    if not valid:
        raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail=message)

    success, message = new_transaction(
        transaction_data=transaction_data, existing_portfolio=existing_data, user_data=UserResponse(**user)
    )
    return {"success": success, "message": message}


async def update_trade(transaction_data: UpdateTrade, user: UserResponse = Depends(authorise_user)) -> BaseResponse:
    success: bool = False
    message: str = "TRANSACTION_SUCCESSFUL"

    valid, message, existing_data = valid_transaction(transaction_data=transaction_data, user_data=UserResponse(**user))
    if not valid:
        raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail=message)

    success, message = update_last_transaction(
        new_transaction_data=transaction_data, existing_portfolio=existing_data, user_data=UserResponse(**user)
    )
    return {"success": success, "message": message}


async def delete_trade(transaction_data: DeleteTrade, user: UserResponse = Depends(authorise_user)) -> BaseResponse:
    success: bool = False
    message: str = "TRANSACTION_SUCCESSFUL"

    success, message = delete_last_transaction(deleting_portfolio_data=transaction_data, user_data=UserResponse(**user))
    return {"success": success, "message": message}


async def get_trades(user: UserResponse = Depends(authorise_user)):
    response = get_all_trades(user_data=UserResponse(**user))
    return response
