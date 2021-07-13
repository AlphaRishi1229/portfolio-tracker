from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Tuple

from fastapi import HTTPException

from models.db_models import Portfolio, Transaction
from tracker.portfolio.helpers.portfolio_db_helpers import (
    create_portfolio,
    get_portfolio_by_id,
    rollback_portfolio,
    update_portfolio,
)
from tracker.transactions.schemas.transaction_schemas import DeleteTrade, TradeTransaction, UpdateTrade
from tracker.users.schemas.user_schemas import UserResponse
from utils.constants import UNPROCESSABLE_ENTITY
from utils.database_utils import get_db_session


def valid_transaction(transaction_data: TradeTransaction, user_data: UserResponse) -> Tuple[bool, str, Portfolio]:
    """Validates the received transaction.

    Args:
        transaction_data (TradeTransaction): The received transaction data.
        user_data (UserResponse): The users information.

    Returns:
        Tuple[bool, str, Portfolio]: A tuple of is_valid, the message and if portfolio exists then portfolio object.
    """
    is_valid: bool = True
    message: str = ""

    session = get_db_session()
    existing_portfolio: Portfolio = session.query(Portfolio).filter(
        Portfolio.security_id == transaction_data.security_id,
        Portfolio.user_id == user_data.id
    ).first()

    if existing_portfolio and transaction_data.transaction_type == "SELL":
        # Check if we have enough quantity to sell.
        if transaction_data.quantity > existing_portfolio.quantity:
            is_valid = False
            message = "NOT_ENOUGH_QUANTITY_TO_SELL"
    if not existing_portfolio and transaction_data.transaction_type == "SELL":
        # If we don't have any quantity.
        is_valid = False
        message = "NO_QUANTITY_AVAILABLE_TO_SELL"

    return (is_valid, message, existing_portfolio)


def create_transaction(
    transaction_data: TradeTransaction, existing_portfolio: Portfolio,
    user_id: int, session = get_db_session()
) -> Tuple[bool, str, str]:
    """Creates a new transaction in database.

    Args:
        transaction_data (TradeTransaction): The data to be added.
        existing_portfolio (Portfolio): Any existing portfolio for the portfolio id.
        user_id (int): The user id.
        session (session, optional): The db session. Defaults to get_db_session().

    Returns:
        Tuple[bool, str, str]: A tuple of is_success, the message and transaction id.
    """
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"
    transaction_id: int = 0

    transaction_data = {
        "portfolio_id": existing_portfolio.id,
        "transaction_type": transaction_data.transaction_type,
        "transaction_amount": transaction_data.transaction_amount,
        "transaction_quantity": transaction_data.quantity,
        "is_valid_trade": True,
        "created_on": datetime.now(),
        "user_id": user_id
    }
    db_transaction: Transaction = Transaction(**transaction_data)

    try:
        session.add(db_transaction)
        session.commit()
        transaction_id = db_transaction.id

    except Exception as e:
        success = False
        message = "TRANSACTION_FAILED"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message, transaction_id


def update_transaction(
    update_data: UpdateTrade, transaction_id: int, new_portfolio_id: int, session = get_db_session()
) -> Tuple[bool, str]:
    """Update the previous transaction entry with a new data.

    Args:
        update_data (UpdateTrade): The data to be updated.
        transaction_id (int): The transaction id to be updated,
        new_portfolio_id (int): The new portfolio id to point that transaction to.
        session ([type], optional): The db session.. Defaults to get_db_session().

    Returns:
        Tuple[bool, str]: A tuple of success and message.
    """
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"

    # Get transaction to be updated.
    transaction_to_update = session.query(Transaction).filter(
        Transaction.id == transaction_id
    )
    update_data = {
        "portfolio_id": new_portfolio_id,
        "transaction_type": update_data.transaction_type,
        "transaction_amount": update_data.transaction_amount,
        "transaction_quantity": update_data.quantity
    }

    try:
        # Update the transaction.
        transaction_to_update.update(
            update_data, synchronize_session="evaluate"
        )
        session.commit()
    except Exception as e:
        success = False
        message = "FAILED_TO_UPDATE_TRANSACTION"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message


def delete_transaction(transaction_id: int, session = get_db_session()) -> Tuple[bool, str]:
    """Delete a transaction by transaction id from a db.

    Args:
        transaction_id (int): The transaction id to be deleted.
        session ([type], optional): The db session. Defaults to get_db_session().

    Returns:
        Tuple[bool, str]: A tuple of success and messgae.
    """
    success: bool = True
    message: str = "DELETION_SUCCESSFUL"

    transaction_to_delete = session.query(Transaction).filter(
        Transaction.id == transaction_id
    ).one()

    try:
        session.delete(transaction_to_delete)
        session.commit()
    except Exception as e:
        success = False
        message = "FAILED_TO_DELETE_TRANSACTION"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message


def new_transaction(
    transaction_data: TradeTransaction, existing_portfolio: Portfolio, user_data: UserResponse
) -> Tuple[bool, str, str]:
    """Adds a new transaction for a security and updates the user's portfolio.

    Args:
        transaction_data (TradeTransaction): The received transaction data.
        existing_portfolio (Portfolio): The portfolio existing in db.
        user_data (UserResponse): The user data.

    Returns:
        Tuple[bool, str, str]: A tuple of is_success, message and transaction id.
    """
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"
    transaction_id: int = 0

    if existing_portfolio:
        # Add new transaction.
        is_success, message, transaction_id = create_transaction(
            transaction_data=transaction_data, existing_portfolio=existing_portfolio,
            user_id=user_data.id, session=session
        )
        if is_success:
            is_success, message = update_portfolio(
                transaction_data=transaction_data, existing_portfolio=existing_portfolio, session=session
            )
    if not existing_portfolio:
        # create new portfolio.
        is_success, message, new_portfolio = create_portfolio(
            transaction_data=transaction_data, user_data=user_data, session=session
        )
        if is_success:
            is_success, message, transaction_id = create_transaction(
                transaction_data=transaction_data, existing_portfolio=new_portfolio,
                user_id=user_data.id, session=session
            )

    return is_success, message, transaction_id


def get_temp_portfolio(old_transaction_data: Transaction, current_portfolio: Portfolio) -> Portfolio:
    """Creates a temporary portfolio with the rolled back data.

    Args:
        old_transaction_data (Transaction): The last transaction data.
        current_portfolio (Portfolio): The current portfolio data to be updated.

    Raises:
        HTTPException: If problems with quantity.

    Returns:
        Portfolio: The temporariy updated portfolio,
    """
    temp_portfolio = deepcopy(current_portfolio)

    if old_transaction_data.transaction_type == "BUY":
        # If transaction was buy then substract it to roll back.
        new_quantity = int(current_portfolio.quantity - old_transaction_data.transaction_quantity)
        if new_quantity > 0:
            last_price = (
            (current_portfolio.average_buy_price * current_portfolio.quantity) -\
                (old_transaction_data.transaction_amount * old_transaction_data.transaction_quantity)
            ) / new_quantity
        elif new_quantity == 0:
            last_price = (
            (current_portfolio.average_buy_price * current_portfolio.quantity) -\
                (old_transaction_data.transaction_amount * old_transaction_data.transaction_quantity)
            ) / 1
        else:
            raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail="TRANSACTION CANNOT BE UPDATED, CHECK QUANTITY")
    else:
        # If had sell the add to roll back the transaction.
        new_quantity = int(current_portfolio.quantity + old_transaction_data.transaction_quantity)
        last_price = (
        (current_portfolio.average_buy_price * current_portfolio.quantity) +\
            (old_transaction_data.transaction_amount * old_transaction_data.transaction_quantity)
        ) / new_quantity

    temp_portfolio.average_buy_price = float("{:.2f}".format(last_price))
    temp_portfolio.quantity = new_quantity

    return temp_portfolio


def update_last_transaction(
    new_transaction_data: UpdateTrade, existing_portfolio: Portfolio, user_data: UserResponse
) -> Tuple[bool, str, str]:
    """The main function that updates the last transaction. Might be complex to understand but lets keep it simple.

    Args:
        new_transaction_data (UpdateTrade): The updating data.
        existing_portfolio (Portfolio): The data of portfolio that needs to be updated with new transaction.
        user_data (UserResponse): The user data.

    Returns:
        Tuple[bool, str, str]: A tuple of is_success, message and a reference id.
    """
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_UPDATED_SUCCESSFULLY"

    # Gets the data of portfolio that needs to be rolled back.
    portfolio_to_update: Portfolio = get_portfolio_by_id(
        portfolio_id=new_transaction_data.updating_portfolio_id, user_id=user_data.id, session=session
    )

    if not portfolio_to_update:
        # If no portfolio found then raise error.
        is_success = False
        message = "INVALID PORTFOLIO ID."
    elif not existing_portfolio:
        # If portfolio to be rollbacked exists but the portfolio to update does not exist.
        # Suppose you bought 5 shares of tcs in last transaction and you need to update that transaction to BUY 2 shares of infosys
        # then portfolio_to_update will be your last tcs transaction
        # and existing_portfolio will be infosys share.
        # But in the past you have never bought infosys share so existing_portfolio will be None.
        last_transaction: Transaction = portfolio_to_update.transactions[-1]  # Last transaction.
        # Create a temporary portfolio with rolled back data.
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_update
        )
        # Rollback your transaction.
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        # Create a new portfolio.
        is_success, message, new_portfolio = create_portfolio(
            transaction_data=new_transaction_data, user_data=user_data, session=session
        )
        if is_success:
            # If portfolio created then update the transaction.
            is_success, message = update_transaction(
                update_data=new_transaction_data, transaction_id=last_transaction.id,
                new_portfolio_id=new_portfolio.id, session=session
            )
    elif existing_portfolio.id:
        # If portfolio to be rollbacked and the portfolio to update exists.
        # Suppose you bought 5 shares of tcs in last transaction and you need to update that transaction to BUY 2 shares of infosys
        # and you have bought both of them in the past.
        # then portfolio_to_update will be your last tcs transaction
        # from 5 shares to 2 shares of infosys.
        last_transaction: Transaction = portfolio_to_update.transactions[-1]  # Last transaction.
        # A temporary portfolio to rollback.
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_update
        )
        # Rollback the portfolio.
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        # Update the old transaction with the new data.
        is_success, message = update_transaction(
            update_data=new_transaction_data, transaction_id=last_transaction.id,
            new_portfolio_id=existing_portfolio.id, session=session
        )
        if is_success and existing_portfolio.id == portfolio_to_update.id:
            # If existing and updating portfolio are same. (tcs and tcs)
            is_success, message = update_portfolio(
                transaction_data=new_transaction_data, existing_portfolio=temp_portfolio, session=session
            )
        elif is_success and existing_portfolio.id != portfolio_to_update.id:
            # If existing and updating portfolio are different. (tcs and infy)
            is_success, message = update_portfolio(
                transaction_data=new_transaction_data, existing_portfolio=existing_portfolio, session=session
            )

    return is_success, message


def delete_last_transaction(deleting_portfolio_data: DeleteTrade, user_data: UserResponse) -> Tuple[bool, str]:
    """The main function that performs the deletion operation on a portfolio's transaction.

    Args:
        deleting_portfolio_data (DeleteTrade): The data to be deleted.
        user_data (UserResponse): The user's data.

    Returns:
        Tuple[bool, str]: A tuple of success and message.
    """
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_DELETED_SUCCESSFULLY"

    portfolio_to_delete: Portfolio = get_portfolio_by_id(
        portfolio_id=deleting_portfolio_data.portfolio_id, user_id=user_data.id, session=session
    )

    if not portfolio_to_delete:
        # If portfolio not found.
        is_success = False
        message = "INVALID PORTFOLIO ID."
    elif not portfolio_to_delete.quantity:
        # If quantity is 0 for that portfolio.
        is_success = False
        message = "NOT ENOUGH QUANTITY TO DELETE."
    else:
        last_transaction: Transaction = portfolio_to_delete.transactions[-1]
        # Create a temp portfolio for rolling back.
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_delete
        )
        # Rollback the portfolio.
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        # Delete the transaction.
        is_success, message = delete_transaction(transaction_id=last_transaction.id, session=session)

    return is_success, message


def get_all_trades(user_data: UserResponse) -> Dict:
    """Gets all the trades for the database against a user id.

    Args:
        user_data (UserResponse): The user for which trades are to be returned.

    Returns:
        Dict: The response dict.
    """
    session = get_db_session()
    response = {}
    portfolio_list: List[Portfolio] = session.query(Portfolio).filter(Portfolio.user_id == user_data.id).all()

    for portfolio in portfolio_list:
        ticker: str = portfolio.security_data.ticker_symbol
        transactions_list: List[Transaction] = portfolio.transactions
        serialised_transactions = []
        for transaction in transactions_list:
            serialised_transactions.append(
                {
                    "transaction_date": transaction.created_on,
                    "transaction_type": transaction.transaction_type,
                    "transaction_quantity": transaction.transaction_quantity,
                    "transaction_amount": transaction.transaction_amount
                }
            )
        response[ticker] = serialised_transactions

    return response
