from typing import List

from fastapi import APIRouter

from tracker.securities.handlers.securities_handler import create_security, security_listing, update_security
from tracker.securities.schemas.security_schemas import BaseResponse, SecurityResponse
from utils.constants import BASE_RESPONSE_STATUS_CODES


security_v1_apis = APIRouter(
    prefix="/api/v1/security",
    tags=["Security related APIs"],
    responses=BASE_RESPONSE_STATUS_CODES,
)

security_v1_apis.add_api_route("/create", create_security, response_model=BaseResponse, methods=["POST"])
security_v1_apis.add_api_route("/update", update_security, response_model=BaseResponse, methods=["POST"])
security_v1_apis.add_api_route("/listing", security_listing, response_model=List[SecurityResponse], methods=["GET"])
