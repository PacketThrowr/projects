from fastapi import APIRouter
from app.auth import fastapi_users, auth_backend
from app.schemas.user import UserRead, UserCreate, LoginSchema

router = APIRouter()

# Replace the default login route with the new schema
router.include_router(
    fastapi_users.get_auth_router(
        auth_backend,
        login_schema=LoginSchema,  # Use the custom schema
    ),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
