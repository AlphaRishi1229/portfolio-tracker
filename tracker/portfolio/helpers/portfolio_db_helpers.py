from datetime import datetime
from typing import Dict, List, Tuple, Union

from models.db_models import Portfolio, Securities
from tracker.transactions.schemas.transaction_schemas import TradeTransaction
from tracker.users.schemas.user_schemas import UserResponse
from utils.database_utils import get_db_session


def create_portfolio(
    transaction_data: TradeTransaction, user_data: UserResponse, session = get_db_session()
) -> Tuple[bool, str, Portfolio]:
    """Creates or adds a new portfolio to the database.

    Args:
        transaction_data (TradeTransaction): The transaction data for the portfolio.
        user_data (UserResponse): The users data.
        session ([type], optional): The db session. Defaults to get_db_session().

    Returns:
        Tuple[bool, str, Portfolio]: A tuple of success, message and new portfolio object.
    """
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"
    portfolio_data = {
        "security_id": transaction_data.security_id,
        "user_id": user_data.id,
        "average_buy_price": transaction_data.transaction_amount,
        "quantity": transaction_data.quantity,
        "created_on": datetime.now(),
        "updated_on": datetime.now()
    }
    db_portfolio: Portfolio = Portfolio(**portfolio_data)

    try:
        session.add(db_portfolio)
        session.commit()
    except Exception as e:
        success = False
        message = "FAILED_TO_CREATE_PORTFOLIO"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message, db_portfolio


def update_portfolio(transaction_data: TradeTransaction, existing_portfolio: Portfolio, session = get_db_session()):
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"
    portfolio_to_update = session.query(Portfolio).filter(
        Portfolio.id == existing_portfolio.id
    )
    update_data = {
        "updated_on": datetime.now()
    }

    if transaction_data.transaction_type == "BUY":
        update_data["quantity"] = int(existing_portfolio.quantity + transaction_data.quantity)
        new_price = (
            (existing_portfolio.average_buy_price * existing_portfolio.quantity) + (transaction_data.transaction_amount * transaction_data.quantity)
        ) / (existing_portfolio.quantity + transaction_data.quantity)
        update_data["average_buy_price"] = float("{:.2f}".format(new_price))
    elif transaction_data.transaction_type == "SELL":
        update_data["quantity"] = int(existing_portfolio.quantity - transaction_data.quantity)

    try:
        portfolio_to_update.update(
            update_data, synchronize_session="evaluate"
        )
        session.commit()
    except Exception as e:
        success = False
        message = "FAILED_TO_UPDATE_PORTFOLIO"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message


def rollback_portfolio(updated_portfolio: Portfolio, session = get_db_session()) -> Tuple[bool, str]:
    """Updates the portfolio with the old transaction data.

    Args:
        updated_portfolio (Portfolio): The updated portfolio data.
        session ([type], optional): The db session. Defaults to get_db_session().

    Returns:
        Tuple[bool, str]: A tuple of success and message.
    """
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"

    portfolio_to_update = session.query(Portfolio).filter(
        Portfolio.id == updated_portfolio.id
    )
    update_data = {
        "updated_on": datetime.now(),
        "quantity": updated_portfolio.quantity,
        "average_buy_price": updated_portfolio.average_buy_price
    }

    try:
        portfolio_to_update.update(
            update_data, synchronize_session="evaluate"
        )
        session.commit()
    except Exception as e:
        success = False
        message = "FAILED_TO_UPDATE_PORTFOLIO"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message


def get_portfolio_by_id(portfolio_id: int, user_id: int, session = get_db_session()) -> Portfolio:
    """Gets data of portfolio against its id.

    Args:
        portfolio_id (int): The portfolio id for which data needs to be returned.
        user_id (int): The user id.
        session ([type], optional): The db session. Defaults to get_db_session().

    Returns:
        Portfolio: [description]
    """
    portfolio: Portfolio = session.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    return portfolio


def get_portfolio_data(user_data: UserResponse) -> List:
    """Returns a list of all the portfolios currently that user holds.

    Args:
        user_data (UserResponse): The user data.

    Returns:
        List: The list of portfolios.
    """
    session = get_db_session()
    response = []
    portfolio_list: List[Portfolio] = session.query(Portfolio).filter(Portfolio.user_id == user_data.id).all()

    for portfolio in portfolio_list:
        security: Securities = portfolio.security_data
        response.append(
            {
                "portfolio_id": portfolio.id,
                "security_name": security.name,
                "ticker_symbol": security.ticker_symbol,
                "average_buy_price": portfolio.average_buy_price,
                "total_available_quantity": portfolio.quantity
            }
        )

    return response


def calculate_portfolio_returns(user_data: UserResponse) -> Dict:
    """Calculates the total returns of the user's holdings.

    Args:
        user_data (UserResponse): The user data.

    Returns:
        Dict: The total returns dict.
    """
    session = get_db_session()
    portfolio_list: List[Portfolio] = session.query(Portfolio).filter(Portfolio.user_id == user_data.id).all()

    total_returns = 0.00
    for portfolio in portfolio_list:
        security: Securities = portfolio.security_data
        total_returns += ((security.current_price - portfolio.average_buy_price) * portfolio.quantity)

    return {"total_returns": total_returns}
