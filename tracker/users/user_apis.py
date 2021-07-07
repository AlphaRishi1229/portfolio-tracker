"""All api's related to user reside over here."""
from fastapi import APIRouter

from tracker.users.handlers.user_handler import authorise_user, create_user
from tracker.users.schemas.user_schemas import UserResponse


user_v1_apis = APIRouter(
    prefix="/api/v1/user",
    tags=["User related APIs"],
    responses={
        401: {"description": "UNAUTHORISED"},
        404: {"description": "INCORRECT_URL"},
        500: {"description": "INTERNAL_SERVER_ERROR"}
    },
)

# Authorisation Api.
user_v1_apis.add_api_route("/auth", authorise_user, response_model=UserResponse, methods=["POST"])
# Create User Api.
user_v1_apis.add_api_route("/create", create_user, response_model=UserResponse, methods=["POST"])
