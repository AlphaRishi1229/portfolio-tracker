from datetime import datetime
from typing import List, Tuple

from models.db_models import Securities
from tracker.securities.schemas.security_schemas import SecurityCreate, SecurityUpdate
from tracker.users.schemas.user_schemas import UserResponse
from utils.constants import INTERNAL_SERVER_ERROR, SUCCESS_STATUS_CODE, UNPROCESSABLE_ENTITY
from utils.database_utils import get_db_session


def get_security_tickers(ticker_list: List[str], session = get_db_session()) -> List:
    """Returns a lits of securities based on the list of ticker_symbols provided.

    Args:
        ticker_list (List[str]): The list of ticker_symbol for which data is required.
        session ([type], optional): A db session object. Defaults to get_db_session().

    Returns:
        List: The list of securities for the tickers mentioned.
    """
    security_list = []
    try:
        security_list = session.query(Securities.ticker_symbol).filter(
            Securities.ticker_symbol.in_(ticker_list)
        ).all()
    except Exception as e:
        print("Exception Raised: ", e)

    return security_list


def model_bulk_securities(security_data: List[SecurityCreate], user_id: int) -> List[Securities]:
    """Creates a list of new securities that need to be added to the database.

    Args:
        security_data (List[SecurityCreate]): The new data received from the user that needs to be modelled.
        user_id (int): The user id performing this operation.

    Returns:
        List[Securities]: The list of Security models which can be bulk inserted in the database.
    """
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


def add_securities(security_data: List[SecurityCreate], user_data: UserResponse) -> Tuple[bool, int, str]:
    """The main function that adds the new list of securities to the database.

    Args:
        security_data (List[SecurityCreate]): The list of new securities that needs to be added.
        user_data (UserResponse): The details of User performing the operation.

    Returns:
        Tuple[bool, int, str]: A tuple of success, status_code and the message.
    """
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
        # Model the user data.
        user_data = UserResponse(**user_data)
        # Model the received security data into the database required model.
        bulk_securities = model_bulk_securities(security_data, user_data.id)
        try:
            # Bulk insert operation on the list of Security models.
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
    """Created a list of objects that needs to be updated in the database.

    Args:
        update_data (List[SecurityUpdate]): The list of objects need to be updated.
        user_id (int): The user performing this operation.

    Returns:
        List: A list of objects that need to be updated in the database modified with some extra required keys.
    """
    bulk_securities = []
    for security in update_data:
        # Add data like updated_on and updated_by.
        db_security = {
            "id": security.id,
            "current_price": security.current_price,
            "updated_on": datetime.now(),
            "updated_by": user_id
        }
        bulk_securities.append(db_security)
    return bulk_securities


def update_securities(update_data: List[SecurityUpdate], user_data: UserResponse) -> Tuple[bool, int, str]:
    """The main function that performs the update operation on the database.

    Args:
        update_data (List[SecurityUpdate]): The list of data that needs to be updated.
        user_data (UserResponse): The details of user updating the data.

    Returns:
        Tuple[bool, int, str]: A tuple of success, status_code and the message.
    """
    success: bool = True
    status_code: int = SUCCESS_STATUS_CODE
    message: str = "DATA_ADDED_SUCCESSFULLY"

    session = get_db_session()
    # Model the user data.
    user_data = UserResponse(**user_data)
    # Models the received payload into the final updated columns.
    final_update_data = model_bulk_update(update_data, user_data.id)

    try:
        # Perform the bulk update operation.
        session.bulk_update_mappings(Securities, final_update_data)
        session.commit()
    except Exception as e:
        print("Exception Raised: ", e)
        success = False
        status_code = INTERNAL_SERVER_ERROR
        message = "INTERNAL_SERVER_ERROR"

    return (success, status_code, message)


def transform_securities(security_data: List[Securities]) -> List:
    """The function transforms the received db data into a json response with the only required values.

    Args:
        security_data (List[Securities]): The list of securities received from db.

    Returns:
        List: A list of transformed securities with mandatory data.
    """
    final_response = []
    for data in security_data:
        # Only show the mandatory data.
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
    """The main function that gets all the data from db and transforms it and returns.

    Args:
        ticker_symbol (str): The ticker for which we need data.

    Returns:
        List: The list of transformed data to be shown to the user.
    """
    session = get_db_session()
    db_security_data = []
    if ticker_symbol:
        # If a ticker symbol is specified only get that specific data.
        db_security_data = session.query(Securities).filter(
            Securities.ticker_symbol == ticker_symbol.upper(),
            Securities.is_active == True
        ).all()
    else:
        # Get all active securities from the database.
        db_security_data = session.query(Securities).filter(Securities.is_active == True).all()

    # Transform the received db data into a list of mandatory data objects.
    response = transform_securities(db_security_data)
    return response
