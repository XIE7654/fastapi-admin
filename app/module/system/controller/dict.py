"""
字典控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.dict import DictService
from app.common.response import success, page_success

# 字典类型路由
router_type = APIRouter()

# 字典数据路由
router_data = APIRouter()


# ==================== 字典类型接口 ====================

@router_type.post("/create", summary="创建字典类型")
async def create_dict_type(
    name: str = Query(..., description="字典名称"),
    type: str = Query(..., description="字典类型"),
    status: int = Query(0, description="状态"),
    remark: str = Query("", description="备注"),
    db: AsyncSession = Depends(get_db),
):
    """创建字典类型"""
    dict_type_id = await DictService.create_dict_type(db, name, type, status, remark)
    return success(data=dict_type_id)


@router_type.put("/update", summary="修改字典类型")
async def update_dict_type(
    id: int = Query(..., description="字典类型ID"),
    name: str = Query(None, description="字典名称"),
    type: str = Query(None, description="字典类型"),
    status: int = Query(None, description="状态"),
    remark: str = Query(None, description="备注"),
    db: AsyncSession = Depends(get_db),
):
    """更新字典类型"""
    await DictService.update_dict_type(db, id, name, type, status, remark)
    return success(data=True)


@router_type.delete("/delete", summary="删除字典类型")
async def delete_dict_type(
    id: int = Query(..., description="字典类型ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除字典类型"""
    await DictService.delete_dict_type(db, id)
    return success(data=True)


@router_type.delete("/delete-list", summary="批量删除字典类型")
async def delete_dict_type_list(
    ids: List[int] = Query(..., description="字典类型ID列表"),
    db: AsyncSession = Depends(get_db),
):
    """批量删除字典类型"""
    await DictService.delete_dict_type_list(db, ids)
    return success(data=True)


@router_type.get("/page", summary="获得字典类型的分页列表")
async def get_dict_type_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="字典名称"),
    type: str = Query(None, description="字典类型"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询字典类型列表"""
    types, total = await DictService.get_dict_type_page(db, page_no, page_size, name, type, status)
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
        page_no=page_no,
        page_size=page_size,
    )


@router_type.get("/get", summary="查询字典类型详细")
async def get_dict_type(
    id: int = Query(..., description="字典类型ID"),
    db: AsyncSession = Depends(get_db),
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


@router_type.get("/simple-list", summary="获得全部字典类型列表")
async def get_simple_dict_type_list(
    db: AsyncSession = Depends(get_db),
):
    """获取全部字典类型列表（包括开启 + 禁用的字典类型，主要用于前端的下拉选项）"""
    types = await DictService.get_all_dict_types(db)
    return success(data=[
        {"id": t.id, "name": t.name, "type": t.type}
        for t in types
    ])


# ==================== 字典数据接口 ====================

@router_data.post("/create", summary="新增字典数据")
async def create_dict_data(
    sort: int = Query(0, description="显示顺序"),
    label: str = Query(..., description="字典标签"),
    value: str = Query(..., description="字典键值"),
    dict_type: str = Query(..., description="字典类型"),
    status: int = Query(0, description="状态"),
    color_type: str = Query(None, description="颜色类型"),
    css_class: str = Query(None, description="CSS类名"),
    remark: str = Query("", description="备注"),
    db: AsyncSession = Depends(get_db),
):
    """创建字典数据"""
    dict_data_id = await DictService.create_dict_data(
        db, sort, label, value, dict_type, status, color_type, css_class, remark
    )
    return success(data=dict_data_id)


@router_data.put("/update", summary="修改字典数据")
async def update_dict_data(
    id: int = Query(..., description="字典数据ID"),
    sort: int = Query(None, description="显示顺序"),
    label: str = Query(None, description="字典标签"),
    value: str = Query(None, description="字典键值"),
    dict_type: str = Query(None, description="字典类型"),
    status: int = Query(None, description="状态"),
    color_type: str = Query(None, description="颜色类型"),
    css_class: str = Query(None, description="CSS类名"),
    remark: str = Query(None, description="备注"),
    db: AsyncSession = Depends(get_db),
):
    """更新字典数据"""
    await DictService.update_dict_data(
        db, id, sort, label, value, dict_type, status, color_type, css_class, remark
    )
    return success(data=True)


@router_data.delete("/delete", summary="删除字典数据")
async def delete_dict_data(
    id: int = Query(..., description="字典数据ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除字典数据"""
    await DictService.delete_dict_data(db, id)
    return success(data=True)


@router_data.delete("/delete-list", summary="批量删除字典数据")
async def delete_dict_data_list(
    ids: List[int] = Query(..., description="字典数据ID列表"),
    db: AsyncSession = Depends(get_db),
):
    """批量删除字典数据"""
    await DictService.delete_dict_data_list(db, ids)
    return success(data=True)


@router_data.get("/simple-list", summary="获得全部字典数据列表")
async def get_simple_dict_data_list(
    db: AsyncSession = Depends(get_db),
):
    """获取全部字典数据列表（一般用于管理后台缓存字典数据在本地，只返回启用状态的数据）"""
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
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    dict_type: str = Query(None, description="字典类型"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询字典数据列表"""
    data_list, total = await DictService.get_dict_data_page(db, page_no, page_size, dict_type, status)
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
        page_no=page_no,
        page_size=page_size,
    )


@router_data.get("/get", summary="查询字典数据详细")
async def get_dict_data(
    id: int = Query(..., description="字典数据ID"),
    db: AsyncSession = Depends(get_db),
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