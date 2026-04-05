from fastapi import APIRouter, Depends

import api.auth.endpoints as auth
import api.buy.endpoints as buy
import api.common.endpoints as common
import api.menu.endpoints as menu
import api.user.endpoints as user
from api import deps

router = APIRouter(dependencies=[Depends(deps.get_authenticated_actor)])
router.include_router(user.router)
router.include_router(menu.router)
router.include_router(buy.router)
router.include_router(common.router)

authrouter = APIRouter()
authrouter.include_router(auth.authrouter)
