"""
数据权限服务
基于部门层级的行级权限过滤
"""
from typing import Optional, List, Set
from enum import IntEnum
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.module.system.model.dept import Dept
from app.module.system.model.role import Role
from app.module.system.model.user import UserRole
from app.module.system.service.dept import DeptService


class DataScope(IntEnum):
    """数据范围枚举"""

    ALL = 1  # 全部数据权限
    CUSTOM = 2  # 自定义数据权限
    DEPT = 3  # 本部门数据权限
    DEPT_AND_CHILD = 4  # 本部门及以下数据权限
    SELF = 5  # 仅本人数据权限


class DataPermissionService:
    """数据权限服务"""

    @staticmethod
    async def get_user_data_scope(
        db: AsyncSession,
        user_id: int,
        tenant_id: int = None
    ) -> tuple[int, List[int]]:
        """
        获取用户的数据权限范围

        Args:
            db: 数据库会话
            user_id: 用户ID
            tenant_id: 租户ID

        Returns:
            (数据范围类型, 部门ID列表)
        """
        # 超级管理员拥有全部权限
        if user_id == 1:
            return DataScope.ALL, []

        # 获取用户的角色
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == user_id,
                Role.deleted == 0,
                Role.status == 0
            )
        )
        roles = result.scalars().all()

        if not roles:
            return DataScope.SELF, []

        # 取最大权限范围
        max_scope = min([r.data_scope for r in roles])  # 数字越小权限越大
        dept_ids = set()

        for role in roles:
            if role.data_scope == DataScope.ALL:
                return DataScope.ALL, []

            elif role.data_scope == DataScope.CUSTOM:
                # 自定义权限
                if role.data_scope_dept_ids:
                    dept_ids.update(role.get_data_scope_dept_ids_list())

            elif role.data_scope == DataScope.DEPT:
                # 本部门权限
                result = await db.execute(
                    select(Dept).join(
                        "system_user",
                        Dept.id == "system_user.dept_id"
                    ).where("system_user.id" == user_id)
                )
                # 需要通过用户表获取部门ID
                from app.module.system.model.user import User
                user_result = await db.execute(
                    select(User.dept_id).where(User.id == user_id)
                )
                dept_id = user_result.scalar_one_or_none()
                if dept_id:
                    dept_ids.add(dept_id)

            elif role.data_scope == DataScope.DEPT_AND_CHILD:
                # 本部门及以下权限
                from app.module.system.model.user import User
                user_result = await db.execute(
                    select(User.dept_id).where(User.id == user_id)
                )
                dept_id = user_result.scalar_one_or_none()
                if dept_id:
                    children = await DeptService.get_children_ids(db, dept_id)
                    dept_ids.update(children)

        return max_scope, list(dept_ids)

    @staticmethod
    def apply_data_permission(
        query: Select,
        model_class,
        user_id: int,
        data_scope: int,
        dept_ids: List[int],
        dept_column: str = "dept_id",
        creator_column: str = "creator",
    ) -> Select:
        """
        应用数据权限过滤

        Args:
            query: SQLAlchemy查询对象
            model_class: 模型类
            user_id: 用户ID
            data_scope: 数据范围类型
            dept_ids: 部门ID列表
            dept_column: 部门字段名
            creator_column: 创建者字段名

        Returns:
            添加了权限过滤的查询对象
        """
        # 全部权限
        if data_scope == DataScope.ALL:
            return query

        # 仅本人权限
        if data_scope == DataScope.SELF:
            return query.filter(getattr(model_class, creator_column) == user_id)

        # 本部门/本部门及以下/自定义权限
        if dept_ids:
            dept_attr = getattr(model_class, dept_column, None)
            if dept_attr is not None:
                return query.filter(dept_attr.in_(dept_ids))

        return query.filter(getattr(model_class, creator_column) == user_id)


async def get_data_permission_filter(
    db: AsyncSession,
    user_id: int,
    model_class,
    dept_column: str = "dept_id",
    creator_column: str = "creator",
) -> Select:
    """
    获取带数据权限过滤的查询构建器

    Args:
        db: 数据库会话
        user_id: 用户ID
        model_class: 模型类
        dept_column: 部门字段名
        creator_column: 创建者字段名

    Returns:
        带权限过滤的基础查询

    Usage:
        query = await get_data_permission_filter(db, user_id, User)
        result = await db.execute(query.where(User.status == 0))
    """
    data_scope, dept_ids = await DataPermissionService.get_user_data_scope(db, user_id)

    query = select(model_class)
    return DataPermissionService.apply_data_permission(
        query,
        model_class,
        user_id,
        data_scope,
        dept_ids,
        dept_column,
        creator_column
    )