"""
分页组件
"""
from typing import Generic, TypeVar, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

T = TypeVar("T")


@dataclass
class PageResult(Generic[T]):
    """分页结果"""

    list: List[T]
    total: int
    page_no: int = 1
    page_size: int = 10

    @property
    def total_pages(self) -> int:
        """总页数"""
        return (self.total + self.page_size - 1) // self.page_size if self.page_size > 0 else 0

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page_no < self.total_pages

    @property
    def has_previous(self) -> bool:
        """是否有上一页"""
        return self.page_no > 1

    def to_dict(self) -> dict:
        return {
            "list": self.list,
            "total": self.total,
            "pageNo": self.page_no,
            "pageSize": self.page_size,
        }


class PageQuery(BaseModel):
    """分页查询参数"""

    page_no: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页大小")

    @property
    def offset(self) -> int:
        """偏移量"""
        return (self.page_no - 1) * self.page_size

    @property
    def limit(self) -> int:
        """限制数量"""
        return self.page_size


class SortQuery(BaseModel):
    """排序查询参数"""

    sort_field: Optional[str] = Field(default=None, description="排序字段")
    sort_order: Optional[str] = Field(default="asc", description="排序方向: asc/desc")

    def get_order_by(self, model_class) -> Optional[Any]:
        """
        获取SQLAlchemy排序对象

        Args:
            model_class: SQLAlchemy模型类

        Returns:
            排序对象或None
        """
        if not self.sort_field:
            return None

        field = getattr(model_class, self.sort_field, None)
        if field is None:
            return None

        if self.sort_order == "desc":
            return field.desc()
        return field.asc()


class PageSortQuery(PageQuery, SortQuery):
    """分页+排序查询参数"""

    pass