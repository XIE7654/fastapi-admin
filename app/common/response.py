"""
统一响应格式
"""
import json
from datetime import datetime, date
from typing import Any, Optional, Generic, TypeVar, List
from dataclasses import dataclass, field
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.exceptions import BusinessException

T = TypeVar("T")


class TimestampEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，将 datetime 序列化为时间戳（毫秒），大整数序列化为字符串"""

    # JavaScript 安全整数范围
    MAX_SAFE_INTEGER = 9007199254740991  # 2^53 - 1
    MIN_SAFE_INTEGER = -9007199254740991  # -(2^53 - 1)

    def default(self, obj):
        if isinstance(obj, datetime):
            # 返回毫秒级时间戳
            return int(obj.timestamp() * 1000)
        elif isinstance(obj, date):
            # 日期也转为时间戳
            return int(datetime.combine(obj, datetime.min.time()).timestamp() * 1000)
        elif isinstance(obj, bytes):
            # bytes 转为字符串或返回 None
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return None
        elif isinstance(obj, int):
            # 大整数转为字符串，避免 JavaScript 精度丢失
            if obj > self.MAX_SAFE_INTEGER or obj < self.MIN_SAFE_INTEGER:
                return str(obj)
        return super().default(obj)


# JavaScript 安全整数范围
MAX_SAFE_INTEGER = 9007199254740991  # 2^53 - 1
MIN_SAFE_INTEGER = -9007199254740991  # -(2^53 - 1)


def convert_big_int_to_str(data: Any) -> Any:
    """
    递归转换大整数为字符串，避免 JavaScript 精度丢失
    """
    if isinstance(data, dict):
        return {k: convert_big_int_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_big_int_to_str(item) for item in data]
    elif isinstance(data, int):
        if data > MAX_SAFE_INTEGER or data < MIN_SAFE_INTEGER:
            return str(data)
    return data


def serialize_data(data: Any) -> Any:
    """
    序列化数据，处理 Pydantic 模型和 datetime 类型

    Args:
        data: 原始数据

    Returns:
        序列化后的数据（datetime 转为时间戳，大整数转为字符串）
    """

    if isinstance(data, BaseModel):
        # Pydantic 模型：先转为字典，再处理 datetime 和大整数
        obj_dict = data.model_dump(by_alias=True)
        obj_dict = convert_big_int_to_str(obj_dict)
        return json.loads(json.dumps(obj_dict, cls=TimestampEncoder))
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        result = {k: serialize_data(v) for k, v in data.items()}
        return convert_big_int_to_str(result)
    elif isinstance(data, datetime):
        return int(data.timestamp() * 1000)
    elif isinstance(data, date):
        return int(datetime.combine(data, datetime.min.time()).timestamp() * 1000)
    elif isinstance(data, bytes):
        # bytes 转为字符串或返回 None
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return None
    elif isinstance(data, int):
        # 大整数转为字符串，避免 JavaScript 精度丢失
        if data > MAX_SAFE_INTEGER or data < MIN_SAFE_INTEGER:
            return str(data)
    return data


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
    # 序列化数据，将 datetime 转为时间戳
    serialized_data = serialize_data(data)
    return Response(code=0, msg=msg, data=serialized_data).to_dict()


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
    # 序列化数据，将 datetime 转为时间戳
    serialized_data = serialize_data(data)
    return Response(code=code, msg=msg, data=serialized_data).to_dict()


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
    # 序列化列表数据，将 datetime 转为时间戳
    serialized_list = serialize_data(list_data)
    return success(data={
        "list": serialized_list,
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