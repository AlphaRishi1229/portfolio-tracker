from typing import List

from fastapi import APIRouter

from tracker.transactions.handlers.transaction_handler import (
    delete_trade, get_trades, new_trade, update_trade
)
from tracker.transactions.schemas.transaction_schemas import BaseResponse
from utils.constants import BASE_RESPONSE_STATUS_CODES


transaction_v1_apis = APIRouter(
    prefix="/api/v1/transaction",
    tags=["Transaction  related APIs"],
    responses=BASE_RESPONSE_STATUS_CODES,
)

transaction_v1_apis.add_api_route("/history", get_trades, methods=["GET"])
transaction_v1_apis.add_api_route("/trade", new_trade, response_model=BaseResponse, methods=["POST"])
transaction_v1_apis.add_api_route("/update", update_trade, response_model=BaseResponse, methods=["PUT"])
transaction_v1_apis.add_api_route("/rollback", delete_trade, response_model=BaseResponse, methods=["DELETE"])
