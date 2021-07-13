from pydantic import BaseModel


class PortfolioDataSchema(BaseModel):
    """The portfolio data schema."""
    portfolio_id: int = 0
    security_name: str = ""
    ticker_symbol: str = ""
    average_buy_price: float = 0.00
    total_available_quantity: int = 0
