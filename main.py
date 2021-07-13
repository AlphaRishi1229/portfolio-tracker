"""The main fastapi server."""
from fastapi import FastAPI

from tracker.portfolio.portfolio_apis import portfolio_v1_apis
from tracker.securities.security_apis import security_v1_apis
from tracker.transactions.transaction_apis import transaction_v1_apis
from tracker.users.user_apis import user_v1_apis


app = FastAPI(
    title="Portfolio Tracker - Smallcase",
    description="""This project keeps a tracks of your portfolio. You can perform transaction all from these api's.""",
    version="1.0.0",
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
    openapi_url="/swagger.json",
)


@app.get("/", tags=["System Check"])
async def root():
    return {"status": True}


app.include_router(user_v1_apis)
app.include_router(security_v1_apis)
app.include_router(transaction_v1_apis)
app.include_router(portfolio_v1_apis)
