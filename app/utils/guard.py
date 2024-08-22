from fastapi import Depends, HTTPException, status

from app.models import User
from app.services.auth import auth_service


class Guard:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    async def is_admin(
        self, current_user: User = Depends(auth_service.get_current_user)
    ) -> User:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Administrator privileges required",
            )
        return current_user


guard = Guard(auth_service)
