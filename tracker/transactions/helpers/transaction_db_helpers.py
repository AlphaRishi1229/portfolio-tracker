from copy import deepcopy
from datetime import datetime
from typing import List, Tuple, Union

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


def valid_transaction(transaction_data: TradeTransaction, user_data: UserResponse):
    is_valid: bool = True
    message: str = ""
    session = get_db_session()
    existing_portfolio: Portfolio = session.query(Portfolio).filter(
        Portfolio.security_id == transaction_data.security_id,
        Portfolio.user_id == user_data.id
    ).first()
    if existing_portfolio and transaction_data.transaction_type == "SELL":
        if transaction_data.quantity > existing_portfolio.quantity:
            is_valid = False
            message = "NOT_ENOUGH_QUANTITY_TO_SELL"
    if not existing_portfolio and transaction_data.transaction_type == "SELL":
        is_valid = False
        message = "NO_QUANTITY_AVAILABLE_TO_SELL"

    return (is_valid, message, existing_portfolio)


def create_transaction(
    transaction_data: TradeTransaction, existing_portfolio: Portfolio,
    user_id: int, session = get_db_session()
):
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"
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
    except Exception as e:
        success = False
        message = "TRANSACTION_FAILED"
        print("Exception Raised: ", e)
        session.rollback()

    return success, message


def update_transaction(
    update_data: UpdateTrade, transaction_id: int, new_portfolio_id: int, session = get_db_session()
):
    success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"

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


def delete_transaction(transaction_id: int, session = get_db_session()):
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


def new_transaction(transaction_data: TradeTransaction, existing_portfolio: Portfolio, user_data: UserResponse):
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_SUCCESSFUL"

    if existing_portfolio:
        # Add new transaction.
        is_success, message = create_transaction(
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
            is_success, message = create_transaction(
                transaction_data=transaction_data, existing_portfolio=new_portfolio,
                user_id=user_data.id, session=session
            )

    return is_success, message


def get_temp_portfolio(old_transaction_data: Transaction, current_portfolio: Portfolio):
    temp_portfolio = deepcopy(current_portfolio)

    if old_transaction_data.transaction_type == "BUY":
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
        new_quantity = int(current_portfolio.quantity + old_transaction_data.transaction_quantity)
        last_price = (
        (current_portfolio.average_buy_price * current_portfolio.quantity) +\
            (old_transaction_data.transaction_amount * old_transaction_data.transaction_quantity)
        ) / new_quantity

    temp_portfolio.average_buy_price = float("{:.2f}".format(last_price))
    temp_portfolio.quantity = new_quantity

    return temp_portfolio


def update_last_transaction(new_transaction_data: UpdateTrade, existing_portfolio: Portfolio, user_data: UserResponse):
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_UPDATED_SUCCESSFULLY"

    portfolio_to_update: Portfolio = get_portfolio_by_id(
        portfolio_id=new_transaction_data.updating_portfolio_id, user_id=user_data.id, session=session
    )

    if not portfolio_to_update:
        is_success = False
        message = "INVALID PORTFOLIO ID."
    elif not existing_portfolio:
        last_transaction: Transaction = portfolio_to_update.transactions[-1]
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_update
        )
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        is_success, message, new_portfolio = create_portfolio(
            transaction_data=new_transaction_data, user_data=user_data, session=session
        )
        if is_success:
            is_success, message = update_transaction(
                update_data=new_transaction_data, transaction_id=last_transaction.id,
                new_portfolio_id=new_portfolio.id, session=session
            )
    elif existing_portfolio.id:
        last_transaction: Transaction = portfolio_to_update.transactions[-1]
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_update
        )
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        is_success, message = update_transaction(
            update_data=new_transaction_data, transaction_id=last_transaction.id,
            new_portfolio_id=existing_portfolio.id, session=session
        )
        if is_success and existing_portfolio.id == portfolio_to_update.id:
            is_success, message = update_portfolio(
                transaction_data=new_transaction_data, existing_portfolio=temp_portfolio, session=session
            )
        elif is_success and existing_portfolio.id != portfolio_to_update.id:
            is_success, message = update_portfolio(
                transaction_data=new_transaction_data, existing_portfolio=existing_portfolio, session=session
            )

    return is_success, message


def delete_last_transaction(deleting_portfolio_data: DeleteTrade, user_data: UserResponse):
    session = get_db_session()
    is_success: bool = True
    message: str = "TRANSACTION_DELETED_SUCCESSFULLY"

    portfolio_to_delete: Portfolio = get_portfolio_by_id(
        portfolio_id=deleting_portfolio_data.portfolio_id, user_id=user_data.id, session=session
    )

    if not portfolio_to_delete:
        is_success = False
        message = "INVALID PORTFOLIO ID."
    elif not portfolio_to_delete.quantity:
        is_success = False
        message = "NOT ENOUGH QUANTITY TO DELETE."
    else:
        last_transaction: Transaction = portfolio_to_delete.transactions[-1]
        temp_portfolio: Portfolio = get_temp_portfolio(
            old_transaction_data=last_transaction, current_portfolio=portfolio_to_delete
        )
        rollback_portfolio(updated_portfolio=temp_portfolio, session=session)
        is_success, message = delete_transaction(transaction_id=last_transaction.id, session=session)

    return is_success, message


def get_all_trades(user_data: UserResponse):
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
