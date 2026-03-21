"""
统一响应格式
"""
from typing import Any, Optional, Generic, TypeVar, List
from dataclasses import dataclass, field
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.exceptions import BusinessException

T = TypeVar("T")


@dataclass
class Response(Generic[T]):
    """统一响应格式"""

    code: int = 0
    msg: str = "success"
    data: Optional[T] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }

    def to_json_response(self) -> JSONResponse:
        return JSONResponse(
            content=self.to_dict(),
            status_code=200,
        )


def success(data: Any = None, msg: str = "success") -> dict:
    """
    成功响应

    Args:
        data: 响应数据
        msg: 响应消息

    Returns:
        响应字典
    """
    # 处理 Pydantic 模型，使用别名序列化
    if isinstance(data, BaseModel):
        data = data.model_dump(by_alias=True)
    return Response(code=0, msg=msg, data=data).to_dict()


def error(
    code: int = 500,
    msg: str = "系统错误",
    data: Any = None
) -> dict:
    """
    错误响应

    Args:
        code: 错误码
        msg: 错误消息
        data: 额外数据

    Returns:
        响应字典
    """
    return Response(code=code, msg=msg, data=data).to_dict()


def page_success(
    list_data: List[Any],
    total: int,
    page_no: int = 1,
    page_size: int = 10
) -> dict:
    """
    分页成功响应

    Args:
        list_data: 列表数据
        total: 总数
        page_no: 当前页码
        page_size: 每页大小

    Returns:
        响应字典
    """
    return success(data={
        "list": list_data,
        "total": total,
        "pageNo": page_no,
        "pageSize": page_size,
    })


async def response_exception_handler(request, exc: BusinessException):
    """
    全局异常处理器

    Args:
        request: 请求对象
        exc: 业务异常

    Returns:
        JSON响应
    """
    return JSONResponse(
        content=error(code=exc.code, msg=exc.message, data=exc.data),
        status_code=200,  # 业务异常返回200，通过code区分
    )