from typing import Dict


SUCCESS_STATUS_CODE: int = 200
INTERNAL_SERVER_ERROR: int = 500
UNPROCESSABLE_ENTITY: int = 422
UNAUTHORISED_CODE: int = 401

BASE_RESPONSE_STATUS_CODES: Dict = {
    401: {"description": "UNAUTHORISED"},
    404: {"description": "INCORRECT_URL"},
    500: {"description": "INTERNAL_SERVER_ERROR"}
}
