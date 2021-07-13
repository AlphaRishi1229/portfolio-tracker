from typing import Dict, List
from fastapi import Depends

from tracker.portfolio.helpers.portfolio_db_helpers import calculate_portfolio_returns, get_portfolio_data
from tracker.portfolio.schemas.portfolio_schemas import PortfolioDataSchema
from tracker.users.schemas.user_schemas import UserResponse
from tracker.users.handlers.user_handler import authorise_user


async def get_portfolio(user: UserResponse = Depends(authorise_user)) -> List[PortfolioDataSchema]:
    """Returns a list of portfolios that the user holds.

    Args:
        user (UserResponse, optional): The user details. Defaults to Depends(authorise_user).

    Returns:
        List[PortfolioDataSchema]: The list of portfolios.
    """
    response = get_portfolio_data(user_data=UserResponse(**user))
    return response


async def get_returns(user: UserResponse = Depends(authorise_user)) -> Dict:
    """Returns the total returns the user has got.

    Args:
        user (UserResponse, optional): The user data. Defaults to Depends(authorise_user).

    Returns:
        Dict: The return json.
    """
    response = calculate_portfolio_returns(user_data=UserResponse(**user))
    return response
