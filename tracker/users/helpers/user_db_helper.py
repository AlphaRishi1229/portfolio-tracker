"""Helper file that holds all the functions required for processing the request."""
from fastapi import HTTPException

from models.db_models import User
from tracker.users.schemas.user_schemas import UserCreate
from tracker.users.helpers.user_utils import hash_generate
from utils.constants import INTERNAL_SERVER_ERROR
from utils.database_utils import get_db_session


def existing_user(user_id: str) -> User:
    """Fetches for the user data using the user id.

    Args:
        user_id (str): The user id to be searched for.

    Raises:
        HTTPException: If exception occues while querying on db.

    Returns:
        User: The data of user from database.
    """
    session = get_db_session()
    user = None
    try:
        # Query for checking user in db.
        user: User = session.query(User).filter(User.userid == user_id).first()
    except Exception as e:
        print("Exception Raised: ", e)
        raise HTTPException(status_code=INTERNAL_SERVER_ERROR, detail="INTERNAL_SERVER_ERROR")

    return user


def add_new_user(new_user: UserCreate) -> User:
    """Adds a new user to the database.

    Args:
        new_user (UserCreate): The data of the new user.

    Raises:
        HTTPException: If exception occurs while adding user to db.

    Returns:
        User: The data of user added in database.
    """
    session = get_db_session()
    user = {}
    try:
        # Adds user data to database.
        db_user = {
            "name": new_user.name,
            "userid": new_user.userid,
            "password": hash_generate(new_user.password),
            "is_active": new_user.is_active,
        }
        user = User(**db_user)
        session.add(user)
        session.commit()
        session.refresh(user)

    except Exception as e:
        print("Exception Raised: ", e)
        raise HTTPException(status_code=INTERNAL_SERVER_ERROR, detail="INTERNAL_SERVER_ERROR")

    return user
