from typing import Dict

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
    """This function handles request to perform a new transaction or a new trade.

    Args:
        transaction_data (TradeTransaction): The major data required for a transaction to complete.
        user (UserResponse, optional): The user performing the transaction. Defaults to Depends(authorise_user).

    Raises:
        HTTPException: If transaction is not valid.

    Returns:
        BaseResponse: The response when transaction is completed.
    """
    success: bool = False
    message: str = "TRANSACTION_SUCCESSFUL"

    valid, message, existing_data = valid_transaction(transaction_data=transaction_data, user_data=UserResponse(**user))
    if not valid:
        raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail=message)

    # Proceed with the transaction.
    success, message, transaction_id = new_transaction(
        transaction_data=transaction_data, existing_portfolio=existing_data, user_data=UserResponse(**user)
    )
    return {"success": success, "message": message, "ref_id": str(transaction_id)}


async def update_trade(transaction_data: UpdateTrade, user: UserResponse = Depends(authorise_user)) -> BaseResponse:
    """Updates the last performed trade.

    Args:
        transaction_data (UpdateTrade): The updating data.
        user (UserResponse, optional): The user data. Defaults to Depends(authorise_user).

    Raises:
        HTTPException: If updating data is not valid.

    Returns:
        BaseResponse: The response with ref id.
    """
    success: bool = False
    message: str = "TRANSACTION_SUCCESSFUL"

    valid, message, existing_data = valid_transaction(transaction_data=transaction_data, user_data=UserResponse(**user))
    if not valid:
        raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail=message)

    # Update the last transaction.
    success, message = update_last_transaction(
        new_transaction_data=transaction_data, existing_portfolio=existing_data, user_data=UserResponse(**user)
    )
    return {"success": success, "message": message, "ref_id": transaction_data.updating_portfolio_id}


async def delete_trade(transaction_data: DeleteTrade, user: UserResponse = Depends(authorise_user)) -> BaseResponse:
    """This function handles the deletion of trade by rollbacking the last transaction.

    Args:
        transaction_data (DeleteTrade): The data to be deleted.
        user (UserResponse, optional): The user's data. Defaults to Depends(authorise_user).

    Returns:
        BaseResponse: The response/
    """
    success: bool = False
    message: str = "DELETION_UNSUCCESSFUL"

    success, message = delete_last_transaction(deleting_portfolio_data=transaction_data, user_data=UserResponse(**user))
    return {"success": success, "message": message}


async def get_trades(user: UserResponse = Depends(authorise_user)) -> Dict:
    """Returns all the trades that are done by this user.

    Args:
        user (UserResponse, optional): The user related data.. Defaults to Depends(authorise_user).

    Returns:
        Dict: A json of ticker_symbol and its respective trades.

    Response Eg:
        {
            "tcs": [
                {
                    "transaction_date": "2021-07-13T01:00:00",
                    "transaction_type": "BUY",
                    "transaction_quantity": 10
                    "transaction_amount": 3542.01
                }
            ]
        }
    """
    response: Dict = get_all_trades(user_data=UserResponse(**user))
    return response
