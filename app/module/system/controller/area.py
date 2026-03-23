"""
地区控制器
"""
from fastapi import APIRouter

from app.common.response import success
from app.core.utils.area_utils import AreaUtils

router = APIRouter()


@router.get("/tree", summary="获得地区树")
async def get_area_tree():
    """获得地区树"""
    tree = AreaUtils.get_area_tree()
    return success(data=tree)