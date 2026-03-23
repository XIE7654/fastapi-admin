"""
通知公告控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.notice import NoticeService
from app.common.response import success, page_success

router = APIRouter()


@router.post("/create", summary="创建通知公告")
async def create_notice(
    title: str = Query(..., description="公告标题"),
    content: str = Query(..., description="公告内容"),
    type: int = Query(..., description="公告类型: 1-通知, 2-公告"),
    status: int = Query(0, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:notice:create")),
):
    """创建通知公告"""
    notice_id = await NoticeService.create(db, title, content, type, status)
    return success(data=notice_id)


@router.put("/update", summary="修改通知公告")
async def update_notice(
    id: int = Query(..., description="公告ID"),
    title: str = Query(None, description="公告标题"),
    content: str = Query(None, description="公告内容"),
    type: int = Query(None, description="公告类型"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:notice:update")),
):
    """更新通知公告"""
    await NoticeService.update(db, id, title, content, type, status)
    return success(data=True)


@router.delete("/delete", summary="删除通知公告")
async def delete_notice(
    id: int = Query(..., description="公告ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:notice:delete")),
):
    """删除通知公告"""
    await NoticeService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得通知公告")
async def get_notice(
    id: int = Query(..., description="公告ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:notice:query")),
):
    """获取通知公告详情"""
    notice = await NoticeService.get_by_id(db, id)
    if not notice:
        return success(data=None)
    return success(data={
        "id": notice.id,
        "title": notice.title,
        "content": notice.content,
        "type": notice.type,
        "status": notice.status,
        "createTime": notice.create_time,
    })


@router.get("/page", summary="获得通知公告分页")
async def get_notice_page(
    page_no: int = Query(1, ge=1, alias="pageNo", description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页数量"),
    title: str = Query(None, description="公告标题"),
    type: int = Query(None, description="公告类型"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:notice:query")),
):
    """分页查询通知公告"""
    notices, total = await NoticeService.get_page(db, page_no, page_size, title, type, status)
    return page_success(
        list_data=[
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "type": n.type,
                "status": n.status,
                "createTime": n.create_time,
            }
            for n in notices
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )