"""The main fastapi server."""
from fastapi import FastAPI

from tracker.users.user_apis import user_v1_apis
from tracker.securities.security_apis import security_v1_apis


app = FastAPI(
    title="Portfolio Tracker - Smallcase",
    description="""This project tracks your portfolio""",
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
