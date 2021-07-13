from typing import List

from fastapi import APIRouter

from tracker.portfolio.handlers.portfolio_handler import get_portfolio, get_returns
from utils.constants import BASE_RESPONSE_STATUS_CODES


portfolio_v1_apis = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["Portfolio related APIs"],
    responses=BASE_RESPONSE_STATUS_CODES,
)

portfolio_v1_apis.add_api_route("/possession", get_portfolio, methods=["GET"])
portfolio_v1_apis.add_api_route("/returns", get_returns, methods=["GET"])
