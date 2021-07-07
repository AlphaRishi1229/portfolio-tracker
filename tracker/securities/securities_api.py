from fastapi import APIRouter

from tracker.securities.handlers.securities_handler import create_security


security_v1_apis = APIRouter(
    prefix="/api/v1/securities",
    tags=["Security related APIs"],
    responses={
        404: {"description": "Url Not found"}
    },
)

security_v1_apis.add_api_route("/create", create_security, methods=["POST"])
