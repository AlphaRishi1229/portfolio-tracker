from datetime import datetime
from typing import List

from models.db_models import Securities
from tracker.securities.schemas.security_schemas import SecurityCreate, SecurityUpdate
from tracker.users.schemas.user_schemas import UserResponse
from utils.constants import INTERNAL_SERVER_ERROR, SUCCESS_STATUS_CODE, UNPROCESSABLE_ENTITY
from utils.database_utils import get_db_session


def get_security_tickers(ticker_list: List[str], session = get_db_session()):
    security_list = []
    try:
        security_list = session.query(Securities.ticker_symbol).filter(
            Securities.ticker_symbol.in_(ticker_list)
        ).all()
    except Exception as e:
        print("Exception Raised: ", e)

    return security_list


def model_bulk_securities(security_data: List[SecurityCreate], user_id: int) -> List[Securities]:
    bulk_securities = []
    for security in security_data:
        db_security = {
            "name": security.name.upper(),
            "ticker_symbol": security.ticker_symbol.upper(),
            "current_price": security.current_price,
            "is_active": True,
            "created_on": datetime.now(),
            "updated_on": datetime.now(),
            "updated_by": user_id
        }
        bulk_securities.append(Securities(**db_security))
    return bulk_securities


def add_securities(security_data: List[SecurityCreate], user_data: UserResponse) -> bool:
    success: bool = True
    status_code: int = SUCCESS_STATUS_CODE
    message: str = "DATA_ADDED_SUCCESSFULLY"
    session = get_db_session()
    ticker_list = [security.ticker_symbol for security in security_data]
    security_list: List[Securities] = get_security_tickers(ticker_list, session)
    if security_list:
        success = False
        status_code = UNPROCESSABLE_ENTITY
        message = f"DATA_ALREADY_PRESENT_FOR: {security_list}"

    else:
        user_data = UserResponse(**user_data)
        bulk_securities = model_bulk_securities(security_data, user_data.id)
        try:
            session.bulk_save_objects(bulk_securities, user_data.id)
            session.commit()
        except Exception as e:
            print("Exception Raised: ", e)
            success = False
            status_code = INTERNAL_SERVER_ERROR
            message = "INTERNAL_SERVER_ERROR"
            session.rollback()

    return (success, status_code, message)


def model_bulk_update(update_data: List[SecurityUpdate], user_id: int) -> List:
    bulk_securities = []
    for security in update_data:
        db_security = {
            "id": security.id,
            "current_price": security.current_price,
            "updated_on": datetime.now(),
            "updated_by": user_id
        }
        bulk_securities.append(db_security)
    return bulk_securities


def update_securities(update_data: List[SecurityUpdate], user_data: UserResponse) -> bool:
    success: bool = True
    status_code: int = SUCCESS_STATUS_CODE
    message: str = "DATA_ADDED_SUCCESSFULLY"

    session = get_db_session()
    user_data = UserResponse(**user_data)
    final_update_data = model_bulk_update(update_data, user_data.id)

    try:
        session.bulk_update_mappings(Securities, final_update_data)
        session.commit()
    except Exception as e:
        print("Exception Raised: ", e)
        success = False
        status_code = INTERNAL_SERVER_ERROR
        message = "INTERNAL_SERVER_ERROR"

    return (success, status_code, message)


def transform_securities(security_data: List[Securities]) -> List:
    final_response = []
    for data in security_data:
        security = {
            "id": data.id,
            "name": data.name,
            "ticker_symbol": data.ticker_symbol,
            "current_price": data.current_price,
            "updated_on": data.updated_on
        }
        final_response.append(security)
    return final_response


def get_security_details(ticker_symbol: str) -> List:
    session = get_db_session()
    db_security_data = []
    if ticker_symbol:
        db_security_data = session.query(Securities).filter(
            Securities.ticker_symbol == ticker_symbol.upper(),
            Securities.is_active == True
        ).all()
    else:
        db_security_data = session.query(Securities).filter(Securities.is_active == True).all()

    response = transform_securities(db_security_data)
    return response
