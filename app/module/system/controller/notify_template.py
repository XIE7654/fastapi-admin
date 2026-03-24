"""
站内信模板控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.system.service.notify_template import NotifyTemplateService, NotifyMessageServiceExt
from app.common.response import success, page_success


# 请求模型
class NotifyTemplateCreateReqVO(BaseModel):
    """站内信模板创建请求"""
    name: str = Field(..., description="模板名称")
    code: str = Field(..., description="模板编码")
    type: int = Field(..., description="模板类型")
    nickname: str = Field(..., description="发送人名称")
    content: str = Field(..., description="模板内容")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")


class NotifyTemplateUpdateReqVO(BaseModel):
    """站内信模板更新请求"""
    id: int = Field(..., description="模板编号")
    name: Optional[str] = Field(None, description="模板名称")
    code: Optional[str] = Field(None, description="模板编码")
    type: Optional[int] = Field(None, description="模板类型")
    nickname: Optional[str] = Field(None, description="发送人名称")
    content: Optional[str] = Field(None, description="模板内容")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


# 站内信模板路由
router_template = APIRouter()

# 站内信消息路由
router_message = APIRouter()


@router_template.post("/create", summary="创建站内信模板")
async def create_notify_template(
    req: NotifyTemplateCreateReqVO = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:notify-template:create")),
):
    """创建站内信模板"""
    template_id = await NotifyTemplateService.create(
        db=db,
        name=req.name,
        code=req.code,
        type=req.type,
        nickname=req.nickname,
        content=req.content,
        status=req.status,
        remark=req.remark,
    )
    return success(data=template_id)


@router_template.put("/update", summary="更新站内信模板")
async def update_notify_template(
    req: NotifyTemplateUpdateReqVO = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:notify-template:update")),
):
    """更新站内信模板"""
    await NotifyTemplateService.update(
        db=db,
        template_id=req.id,
        name=req.name,
        code=req.code,
        type=req.type,
        nickname=req.nickname,
        content=req.content,
        status=req.status,
        remark=req.remark,
    )
    return success(data=True)


@router_template.delete("/delete", summary="删除站内信模板")
async def delete_notify_template(
    id: int = Query(..., description="模板编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:notify-template:delete")),
):
    """删除站内信模板"""
    await NotifyTemplateService.delete(db, id)
    return success(data=True)


@router_template.delete("/delete-list", summary="批量删除站内信模板")
async def delete_notify_template_list(
    ids: List[int] = Query(..., description="模板编号列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:notify-template:delete")),
):
    """批量删除站内信模板"""
    count = await NotifyTemplateService.delete_list(db, ids)
    return success(data=count)


@router_template.get("/page", summary="获得站内信模板分页")
async def get_notify_template_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="模板名称"),
    code: str = Query(None, description="模板编码"),
    status: int = Query(None, description="状态"),
    type: int = Query(None, description="类型"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:notify-template:query")),
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
    _: User = Depends(check_permission("system:notify-template:query")),
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
    _: User = Depends(check_permission("system:notify-message:query")),
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