from typing import List
from fastapi import APIRouter

from tracker.portfolio.handlers.portfolio_handler import get_portfolio, get_returns
from tracker.portfolio.schemas.portfolio_schemas import PortfolioDataSchema
from utils.constants import BASE_RESPONSE_STATUS_CODES


portfolio_v1_apis = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["Portfolio related APIs"],
    responses=BASE_RESPONSE_STATUS_CODES,
)

# Returns all the holdings the user has.
portfolio_v1_apis.add_api_route("/holdings", get_portfolio, response_model=List[PortfolioDataSchema], methods=["GET"])
# Returns the total return amount user has.
portfolio_v1_apis.add_api_route("/returns", get_returns, methods=["GET"])
