from typing import List

from fastapi import Depends, HTTPException

from tracker.securities.schemas.security_schemas import BaseResponse, SecurityCreate, SecurityResponse, SecurityUpdate
from tracker.securities.helpers.security_db_helpers import add_securities, get_security_details, update_securities
from tracker.users.handlers.user_handler import authorise_user


async def create_security(security_data: List[SecurityCreate], user = Depends(authorise_user)) -> BaseResponse:
    """Handler function that creates a security (share, fund, etc.)

    Args:
        security_data (List[SecurityCreate]): The list of securities to be added.
        user (User, optional): The user details who is adding to the database. Defaults to Depends(authorise_user).

    Raises:
        HTTPException: If faiiled to add data to database.
        Possibilities:
        1) Data already present in db.
        2) Database Internal Exception.

    Returns:
        BaseResponse (Dict): The response.
    """
    success, status_code, message = add_securities(security_data=security_data, user_data=user)
    if not success:
        raise HTTPException(status_code=status_code, detail=message)
    return {
        "success": success,
        "message": message
    }


async def update_security(updating_data: List[SecurityUpdate], user = Depends(authorise_user)) -> BaseResponse:
    """The handler function that updates the current price of the security defined.

    Args:
        updating_data (List[SecurityUpdate]): The list of securites to be updated alongwith the current_price.
        user (User, optional): The user data who is updating. Defaults to Depends(authorise_user).

    Raises:
        HTTPException: If any internal server error occurs.

    Returns:
        BaseResponse (Dict): The success response if data updated successfully.
    """
    success, status_code, message = update_securities(update_data=updating_data, user_data=user)
    if not success:
        raise HTTPException(status_code=status_code, detail=message)
    return {
        "success": success,
        "message": message
    }


async def security_listing(ticker_symbol: str = "") -> List[SecurityResponse]:
    """The handler that lists all the active securities in the database.

    Args:
        ticker_symbol (str, optional): The ticker symbol. Eg: TCS. Defaults to "".

    Returns:
        SecurityResponse (List): The list of all the securities alongwith its data.
    """
    response: List = get_security_details(ticker_symbol=ticker_symbol)
    return response
