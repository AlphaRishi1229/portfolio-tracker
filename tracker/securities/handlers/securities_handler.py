from fastapi import Request

from tracker.securities.schemas.request_schemas import UserCreate


async def create_security(user: UserCreate):
    pass