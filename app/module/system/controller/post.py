"""
岗位控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.post import PostService
from app.module.system.schema.post import PostSave, PostPageQuery
from app.common.response import success, page_success

router = APIRouter()


@router.post("/create", summary="创建岗位")
async def create_post(
    req: PostSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:create")),
):
    """创建岗位"""
    post_id = await PostService.create(db, req.name, req.code, req.sort, req.remark)
    return success(data=post_id)


@router.put("/update", summary="修改岗位")
async def update_post(
    req: PostSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:update")),
):
    """更新岗位"""
    if not req.id:
        return success(data=False, message="岗位ID不能为空")
    await PostService.update(db, req.id, req.name, req.code, req.sort, req.remark)
    return success(data=True)


@router.delete("/delete", summary="删除岗位")
async def delete_post(
    id: int = Query(..., description="岗位ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:delete")),
):
    """删除岗位"""
    await PostService.delete(db, id)
    return success(data=True)


@router.delete("/delete-list", summary="批量删除岗位")
async def delete_post_list(
    ids: List[int] = Query(..., description="岗位ID列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:delete")),
):
    """批量删除岗位"""
    await PostService.delete_list(db, ids)
    return success(data=True)


@router.get("/get", summary="获得岗位信息")
async def get_post(
    id: int = Query(..., description="岗位ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:query")),
):
    """根据ID获取岗位详情"""
    post = await PostService.get_by_id(db, id)
    if not post:
        return success(data=None)
    return success(data={
        "id": post.id,
        "name": post.name,
        "code": post.code,
        "sort": post.sort,
        "status": post.status,
        "remark": post.remark,
        "createTime": post.create_time,
    })


@router.get("/page", summary="获得岗位分页")
async def get_post_page(
    query: PostPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:post:query")),
):
    """分页查询岗位列表"""
    posts, total = await PostService.get_page(db, query.page_no, query.page_size, query.name, query.code, query.status)
    return page_success(
        list_data=[
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "sort": p.sort,
                "status": p.status,
                "remark": p.remark,
                "createTime": p.create_time,
            }
            for p in posts
        ],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获取岗位精简信息列表")
async def get_simple_post_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取岗位精简信息列表（只包含被开启的岗位，主要用于前端的下拉选项）"""
    posts = await PostService.get_all(db)
    # 过滤启用的岗位并按sort排序
    enabled_posts = sorted([p for p in posts if p.status == 0], key=lambda x: x.sort)
    return success(data=[
        {"id": p.id, "name": p.name, "code": p.code}
        for p in enabled_posts
    ])