"""
AI 写作控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWriteController
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.write import WriteService
from app.module.ai.schema.write import (
    WritePageQuery,
    WriteResponse,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.get("/page", summary="获得写作分页")
async def get_write_page(
    query: WritePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:write:query")),
):
    """分页查询写作列表"""
    writes, total = await WriteService.get_page(db, query)
    write_responses = [WriteResponse.model_validate(w) for w in writes]
    return page_success(
        list_data=write_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.delete("/delete", summary="删除写作")
@operate_log(type="AI 写作管理", sub_type="删除写作")
async def delete_write(
    request: Request,
    id: int = Query(..., description="写作编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:write:delete")),
):
    """删除写作"""
    await WriteService.delete(db, id)
    return success(data=True)