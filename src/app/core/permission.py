from fastapi import Depends, HTTPException, status

from api.deps import get_authenticated_user
from app.constant import FORBIDDEN
from auth.dto import AuthenticatedUser


def require_roles(payment_role_ids: list[int]):
    async def role_checker(
        current_user: AuthenticatedUser = Depends(get_authenticated_user),
    ):
        if current_user.role_id not in payment_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=FORBIDDEN,
            )

        return current_user

    return role_checker
