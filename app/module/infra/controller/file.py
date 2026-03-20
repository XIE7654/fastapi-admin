"""
文件控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.infra.service.file import FileService, FileConfigService
from app.common.response import success, page_success

router = APIRouter()


@router.get("/page", summary="获得文件分页")
async def get_file_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    path: str = Query(None, description="文件路径"),
    type: str = Query(None, description="文件类型"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:file:query")),
):
    """分页查询文件列表"""
    files, total = await FileService.get_page(db, page_no, page_size, path, type)
    return page_success(
        list_data=[
            {
                "id": f.id,
                "configId": f.config_id,
                "name": f.name,
                "path": f.path,
                "url": f.url,
                "type": f.type,
                "size": f.size,
                "createTime": f.create_time,
            }
            for f in files
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router.get("/get", summary="获得文件")
async def get_file(
    id: int = Query(..., description="文件ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:file:query")),
):
    """获取文件详情"""
    file = await FileService.get_by_id(db, id)
    if not file:
        return success(data=None)
    return success(data={
        "id": file.id,
        "configId": file.config_id,
        "name": file.name,
        "path": file.path,
        "url": file.url,
        "type": file.type,
        "size": file.size,
        "createTime": file.create_time,
    })


@router.delete("/delete", summary="删除文件")
async def delete_file(
    id: int = Query(..., description="文件ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:file:delete")),
):
    """删除文件"""
    await FileService.delete(db, id)
    return success(data=True)


# 文件配置接口
config_router = APIRouter()


@config_router.get("/list-all-simple", summary="获取文件配置列表")
async def get_file_config_list(
    db: AsyncSession = Depends(get_db),
):
    """获取所有文件配置"""
    configs = await FileConfigService.get_all(db)
    return success(data=[
        {
            "id": c.id,
            "name": c.name,
            "storage": c.storage,
            "master": c.master,
        }
        for c in configs
    ])