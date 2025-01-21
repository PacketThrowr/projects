from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.manager import BaseUserManager
from app.adapters.user import get_user_db
from app.schemas.user import UserRead, UserCreate
from app.models.user import User
from app.utils.security import verify_password
from fastapi import Depends
from typing import Any

SECRET_KEY = "your_secret_key"  # Replace with a strong and secure secret key

# Define a Bearer transport for authentication
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Define the JWT strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

# Custom UserManager to use username for authentication
class CustomUserManager(BaseUserManager[User, int]):
    user_db_model = User

    async def on_after_register(self, user: User, request: Any = None):
        print(f"User {user.username} has registered.")

    async def authenticate(self, credentials):
        user = await self.user_db.get_by_username(credentials.username)
        if user is None:
            return None
        if not verify_password(credentials.password, user.hashed_password):
            return None
        return user

    def parse_id(self, user_id: str) -> int:
        try:
            return int(user_id)
        except ValueError:
            raise ValueError("Invalid user ID format")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield CustomUserManager(user_db)

# Authentication backend using Bearer transport and JWT strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Initialize CustomUserManager
async def get_user_manager(user_db=Depends(get_user_db)):
    yield CustomUserManager(user_db)

# FastAPI Users setup with custom UserManager
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependency for getting the current active user
current_active_user = fastapi_users.current_user(active=True)
