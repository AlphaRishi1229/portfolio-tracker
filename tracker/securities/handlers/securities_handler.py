from typing import List

from fastapi import Depends, HTTPException

from tracker.securities.schemas.security_schemas import SecurityCreate, SecurityUpdate
from tracker.securities.helpers.security_db_helpers import add_securities, get_security_details, update_securities
from tracker.users.handlers.user_handler import authorise_user


async def create_security(security_data: List[SecurityCreate], user = Depends(authorise_user)):
    success, status_code, message = add_securities(security_data=security_data, user_data=user)
    if not success:
        raise HTTPException(status_code=status_code, detail=message)
    return {
        "success": success,
        "message": message
    }


async def update_security(updating_data: List[SecurityUpdate], user = Depends(authorise_user)):
    success, status_code, message = update_securities(update_data=updating_data, user_data=user)
    if not success:
        raise HTTPException(status_code=status_code, detail=message)
    return {
        "success": success,
        "message": message
    }


async def security_listing(ticker_symbol: str = ""):
    response = get_security_details(ticker_symbol=ticker_symbol)
    return response
