"""
地区控制器
"""
from fastapi import APIRouter, Depends

from app.common.response import success
from app.core.utils.area_utils import AreaUtils
from app.core.dependencies import get_current_user
from app.module.system.model.user import User

router = APIRouter()


@router.get("/tree", summary="获得地区树")
async def get_area_tree(
    current_user: User = Depends(get_current_user),
):
    """获得地区树"""
    tree = AreaUtils.get_area_tree()
    return success(data=tree)