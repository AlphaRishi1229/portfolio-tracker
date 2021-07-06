"""The main fastapi server."""
from fastapi import FastAPI

# from urls import blogs_api_router, websocket_v1_router


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


# app.include_router(blogs_api_router)
# app.include_router(websocket_v1_router)
