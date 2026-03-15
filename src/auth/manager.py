from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from .models import User, get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.email} with user_id={user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
