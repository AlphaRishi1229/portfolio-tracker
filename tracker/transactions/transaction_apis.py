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

# Returns all the trades done.
transaction_v1_apis.add_api_route("/history", get_trades, methods=["GET"])
# To perform a new transaction or trade.
transaction_v1_apis.add_api_route("/trade", new_trade, response_model=BaseResponse, methods=["POST"])
# To update the last transaction.
transaction_v1_apis.add_api_route("/update", update_trade, response_model=BaseResponse, methods=["PUT"])
# To delete the last transaction.
transaction_v1_apis.add_api_route("/rollback", delete_trade, response_model=BaseResponse, methods=["DELETE"])
