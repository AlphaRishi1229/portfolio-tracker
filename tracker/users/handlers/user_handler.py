"""Handler file that handles all the requests received on user api's."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from tracker.users.helpers.user_db_helper import add_new_user, existing_user
from tracker.users.schemas.user_schemas import UserCreate, UserResponse
from tracker.users.helpers.user_utils import authorised
from utils.constants import UNAUTHORISED_CODE, UNPROCESSABLE_ENTITY


security = HTTPBasic()

async def create_user(user: UserCreate) -> UserResponse:
    """Creates a user and adds an entry to the database.

    Args:
        user (UserCreate): The serialised request payload.

    Raises:
        HTTPException: If user already exists.

    Returns:
        Response: The response to be given after successful creation.
    """
    new_user = {}
    if existing_user(user.userid):
        # If user already exists in database then raise Http Exception.
        raise HTTPException(status_code=UNPROCESSABLE_ENTITY, detail="USER_ALREADY_EXISTS")
    else:
        # If new user add to database.
        user = add_new_user(user)

    new_user = {
        "id": user.id,
        "name": user.name,
        "userid": user.userid,
        "is_active": user.is_active
    }
    return new_user


async def authorise_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserResponse:
    """The following function is responsible for maintaining the users authorisation.

    Args:
        credentials (HTTPBasicCredentials, optional): The username and password. Defaults to Depends(security).

    Raises:
        HTTPException: If user does not exist.
        HTTPException: If incorrect username or password.

    Returns:
        UserResponse: The response to be given if user is authorised.
    """
    authorised_user = {}
    cur_username = credentials.username
    cur_password = credentials.password
    user = existing_user(cur_username)
    if not user:
        # If no user is returned from the database.
        raise HTTPException(status_code=UNAUTHORISED_CODE, detail="USER_NOT_FOUND")
    elif not authorised(cur_username, cur_password, user.userid, user.password):
        # If username or password is incorrect.
        raise HTTPException(status_code=UNAUTHORISED_CODE, detail="INCORRECT_USER_NAME_OR_PASSWORD")

    authorised_user = {
        "id": user.id,
        "name": user.name,
        "userid": user.userid,
        "is_active": user.is_active
    }
    return authorised_user
