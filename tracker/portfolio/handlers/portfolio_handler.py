from typing import List

from fastapi import Depends

from tracker.portfolio.helpers.portfolio_db_helpers import calculate_portfolio_returns, get_portfolio_data
from tracker.users.schemas.user_schemas import UserResponse
from tracker.users.handlers.user_handler import authorise_user


async def get_portfolio(user: UserResponse = Depends(authorise_user)):
    response = get_portfolio_data(user_data=UserResponse(**user))
    return response


async def get_returns(user: UserResponse = Depends(authorise_user)):
    response = calculate_portfolio_returns(user_data=UserResponse(**user))
    return response
