from fastapi import APIRouter, Depends, HTTPException, Request, Form
from app.auth.backend import fastapi_users, auth_backend, get_user_manager
from app.schemas.user import UserRead, UserCreate, LoginSchema
from fastapi_users.manager import BaseUserManager
from fastapi_users import exceptions
from fastapi_users.authentication import BearerTransport, AuthenticationBackend
from app.models.user import User
from app.utils.security import verify_password
import logging
logger = logging.getLogger("uvicorn.error")  # Use Uvicorn's logger
router = APIRouter()

@router.post("/auth/jwt/login")
async def custom_login_route(
    username: str = Form(...),
    password: str = Form(...),
    user_manager: BaseUserManager[User, int] = Depends(get_user_manager),
    backend: AuthenticationBackend = Depends(lambda: auth_backend),
):
    try:
        logger.info(f"Received login request for username: {username}")

        # Authenticate the user
        user = await user_manager.user_db.get_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(
                status_code=401,
                detail="User not found. Please check your username.",
            )

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            raise HTTPException(
                status_code=401,
                detail="Incorrect password. Please try again.",
            )

        logger.info(f"User authenticated successfully: {username}")

        # Use the JWT strategy from the backend to generate a token
        jwt_strategy = backend.get_strategy()
        token = await jwt_strategy.write_token(user)

        return {"access_token": token, "token_type": "bearer"}

    except HTTPException as http_exc:
        # Let FastAPI handle it, with detailed error messages
        raise http_exc
    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)