"""
站内信模板控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.module.system.service.notify_template import NotifyTemplateService, NotifyMessageServiceExt
from app.common.response import success, page_success

# 站内信模板路由
router_template = APIRouter()

# 站内信消息路由
router_message = APIRouter()


@router_template.get("/page", summary="获得站内信模板分页")
async def get_notify_template_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="模板名称"),
    code: str = Query(None, description="模板编码"),
    status: int = Query(None, description="状态"),
    type: int = Query(None, description="类型"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询站内信模板"""
    templates, total = await NotifyTemplateService.get_page(
        db, page_no, page_size, name, code, status, type
    )
    return page_success(
        list_data=[
            {
                "id": t.id,
                "name": t.name,
                "code": t.code,
                "nickname": t.nickname,
                "content": t.content,
                "type": t.type,
                "params": t.params,
                "status": t.status,
                "remark": t.remark,
                "createTime": t.create_time,
            }
            for t in templates
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_template.get("/get", summary="获得站内信模板")
async def get_notify_template(
    id: int = Query(..., description="模板编号"),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取站内信模板详情"""
    template = await NotifyTemplateService.get_by_id(db, id)
    if not template:
        return success(data=None)
    return success(data={
        "id": template.id,
        "name": template.name,
        "code": template.code,
        "nickname": template.nickname,
        "content": template.content,
        "type": template.type,
        "params": template.params,
        "status": template.status,
        "remark": template.remark,
        "createTime": template.create_time,
    })


@router_message.get("/page", summary="获得站内信消息分页")
async def get_notify_message_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户编号"),
    user_type: int = Query(None, description="用户类型"),
    read_status: int = Query(None, description="阅读状态"),
    template_code: str = Query(None, description="模板编码"),
    template_type: int = Query(None, description="模板类型"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询站内信消息"""
    messages, total = await NotifyMessageServiceExt.get_page(
        db, page_no, page_size, user_id, user_type, read_status, template_code, template_type
    )
    return page_success(
        list_data=[
            {
                "id": m.id,
                "userId": m.user_id,
                "userType": m.user_type,
                "templateId": m.template_id,
                "templateCode": m.template_code,
                "templateNickname": m.template_nickname,
                "templateContent": m.template_content,
                "templateType": m.template_type,
                "templateParams": m.template_params,
                "readStatus": m.read_status == 1,
                "readTime": m.read_time,
                "createTime": m.create_time,
            }
            for m in messages
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )