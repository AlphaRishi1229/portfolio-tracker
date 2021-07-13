from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
TRANSACTION_TYPES = ("BUY", "SELL")


class Securities(Base):
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    ticker_symbol = Column(String, index=True, unique=True, nullable=False)
    current_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, index=True)
    updated_by = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint(name, ticker_symbol, name='_security_uc'),
        Index("ix_active_ticker", "ticker_symbol", "is_active"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    userid = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.now)
    portfolios = relationship("Portfolio", backref="portfolios")

    __table_args__ = (
        UniqueConstraint(name, userid, password, name='_user_uc'),
        Index("ix_active_user", "userid", "is_active"),
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"))
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    average_buy_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now)
    security_data = relationship("Securities", backref="securities")
    transactions = relationship("Transaction", backref="transactions")

    __table_args__ = (
        UniqueConstraint(security_id, user_id, name='_portfolio_uc'),
        Index("ix_user_security", "security_id", "user_id"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    transaction_type = Column(ENUM(*TRANSACTION_TYPES, name="transaction_type_enum"), index=True)
    transaction_amount = Column(Float, nullable=False)
    transaction_quantity = Column(Integer)
    is_valid_trade = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    __table_args__ = (
        Index("ix_valid_transactions", "portfolio_id", "is_valid_trade"),
    )
