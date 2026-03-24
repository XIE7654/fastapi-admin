"""
字典控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.dict import DictService
from app.module.system.schema.dict import DictTypeSave, DictDataSave, DictTypePageQuery, DictDataPageQuery
from app.common.response import success, page_success

# 字典类型路由
router_type = APIRouter()

# 字典数据路由
router_data = APIRouter()


# ==================== 字典类型接口 ====================

@router_type.post("/create", summary="创建字典类型")
async def create_dict_type(
    req: DictTypeSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:create")),
):
    """创建字典类型"""
    dict_type_id = await DictService.create_dict_type(db, req.name, req.type, req.status, req.remark)
    return success(data=dict_type_id)


@router_type.put("/update", summary="修改字典类型")
async def update_dict_type(
    req: DictTypeSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:update")),
):
    """更新字典类型"""
    if not req.id:
        return success(data=False, message="字典类型ID不能为空")
    await DictService.update_dict_type(db, req.id, req.name, req.type, req.status, req.remark)
    return success(data=True)


@router_type.delete("/delete", summary="删除字典类型")
async def delete_dict_type(
    id: int = Query(..., description="字典类型ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:delete")),
):
    """删除字典类型"""
    await DictService.delete_dict_type(db, id)
    return success(data=True)


@router_type.delete("/delete-list", summary="批量删除字典类型")
async def delete_dict_type_list(
    ids: List[int] = Query(..., description="字典类型ID列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:delete")),
):
    """批量删除字典类型"""
    await DictService.delete_dict_type_list(db, ids)
    return success(data=True)


@router_type.get("/page", summary="获得字典类型的分页列表")
async def get_dict_type_page(
    query: DictTypePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:query")),
):
    """分页查询字典类型列表"""
    types, total = await DictService.get_dict_type_page(db, query.page_no, query.page_size, query.name, query.type, query.status)
    return page_success(
        list_data=[
            {
                "id": t.id,
                "name": t.name,
                "type": t.type,
                "status": t.status,
                "remark": t.remark,
                "createTime": t.create_time,
            }
            for t in types
        ],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router_type.get("/get", summary="查询字典类型详细")
async def get_dict_type(
    id: int = Query(..., description="字典类型ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:query")),
):
    """根据ID获取字典类型详情"""
    dict_type = await DictService.get_dict_type_by_id(db, id)
    if not dict_type:
        return success(data=None)
    return success(data={
        "id": dict_type.id,
        "name": dict_type.name,
        "type": dict_type.type,
        "status": dict_type.status,
        "remark": dict_type.remark,
        "createTime": dict_type.create_time,
    })


async def _get_simple_dict_type_list(db: AsyncSession):
    """获取全部字典类型列表（包括开启 + 禁用的字典类型，主要用于前端的下拉选项）无需登录认证"""
    types = await DictService.get_all_dict_types(db)
    return success(data=[
        {"id": t.id, "name": t.name, "type": t.type}
        for t in types
    ])


@router_type.get("/simple-list", summary="获得全部字典类型列表")
async def get_simple_dict_type_list(
    db: AsyncSession = Depends(get_db),
):
    """获取全部字典类型列表"""
    return await _get_simple_dict_type_list(db)


@router_type.get("/list-all-simple", summary="获得全部字典类型列表")
async def get_list_all_simple(
    db: AsyncSession = Depends(get_db),
):
    """获取全部字典类型列表（包括开启 + 禁用的字典类型，主要用于前端的下拉选项）无需登录认证"""
    return await _get_simple_dict_type_list(db)


# ==================== 字典数据接口 ====================

@router_data.post("/create", summary="新增字典数据")
async def create_dict_data(
    req: DictDataSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:create")),
):
    """创建字典数据"""
    dict_data_id = await DictService.create_dict_data(
        db, req.sort, req.label, req.value, req.dict_type, req.status, req.color_type, req.css_class, req.remark
    )
    return success(data=dict_data_id)


@router_data.put("/update", summary="修改字典数据")
async def update_dict_data(
    req: DictDataSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:update")),
):
    """更新字典数据"""
    if not req.id:
        return success(data=False, message="字典数据ID不能为空")
    await DictService.update_dict_data(
        db, req.id, req.sort, req.label, req.value, req.dict_type, req.status, req.color_type, req.css_class, req.remark
    )
    return success(data=True)


@router_data.delete("/delete", summary="删除字典数据")
async def delete_dict_data(
    id: int = Query(..., description="字典数据ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:delete")),
):
    """删除字典数据"""
    await DictService.delete_dict_data(db, id)
    return success(data=True)


@router_data.delete("/delete-list", summary="批量删除字典数据")
async def delete_dict_data_list(
    ids: List[int] = Query(..., description="字典数据ID列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:delete")),
):
    """批量删除字典数据"""
    await DictService.delete_dict_data_list(db, ids)
    return success(data=True)


@router_data.get("/simple-list", summary="获得全部字典数据列表")
async def get_simple_dict_data_list(
    db: AsyncSession = Depends(get_db),
):
    """获取全部字典数据列表（一般用于管理后台缓存字典数据在本地，只返回启用状态的数据）无需登录认证"""
    data_list = await DictService.get_all_dict_data(db, status=0)
    return success(data=[
        {
            "dictType": d.dict_type,
            "value": d.value,
            "label": d.label,
            "colorType": d.color_type,
            "cssClass": d.css_class,
        }
        for d in data_list
    ])


@router_data.get("/page", summary="获得字典数据的分页")
async def get_dict_data_page(
    query: DictDataPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:query")),
):
    """分页查询字典数据列表"""
    data_list, total = await DictService.get_dict_data_page(db, query.page_no, query.page_size, query.dict_type, query.label, query.status)
    return page_success(
        list_data=[
            {
                "id": d.id,
                "sort": d.sort,
                "label": d.label,
                "value": d.value,
                "dictType": d.dict_type,
                "status": d.status,
                "colorType": d.color_type,
                "cssClass": d.css_class,
                "remark": d.remark,
                "createTime": d.create_time,
            }
            for d in data_list
        ],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router_data.get("/get", summary="查询字典数据详细")
async def get_dict_data(
    id: int = Query(..., description="字典数据ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dict:query")),
):
    """根据ID获取字典数据详情"""
    dict_data = await DictService.get_dict_data_by_id(db, id)
    if not dict_data:
        return success(data=None)
    return success(data={
        "id": dict_data.id,
        "sort": dict_data.sort,
        "label": dict_data.label,
        "value": dict_data.value,
        "dictType": dict_data.dict_type,
        "status": dict_data.status,
        "colorType": dict_data.color_type,
        "cssClass": dict_data.css_class,
        "remark": dict_data.remark,
        "createTime": dict_data.create_time,
    })