"""
角色服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.role import Role, RoleMenu
from app.module.system.model.user import UserRole
from app.core.exceptions import BusinessException, ErrorCode


class RoleService:
    """角色服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Role]:
        """根据编码获取角色"""
        result = await db.execute(
            select(Role).where(Role.code == code, Role.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
        """获取用户角色列表"""
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Role.deleted == 0, Role.status == 0)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Role]:
        """获取所有角色"""
        result = await db.execute(
            select(Role)
            .where(Role.deleted == 0)
            .order_by(Role.sort.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Role], int]:
        """分页查询角色"""
        query = select(Role).where(Role.deleted == 0)

        if name:
            query = query.where(Role.name.like(f"%{name}%"))
        if code:
            query = query.where(Role.code.like(f"%{code}%"))
        if status is not None:
            query = query.where(Role.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(Role.sort.asc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        roles = result.scalars().all()

        return list(roles), total

    @staticmethod
    async def get_role_menu_ids(db: AsyncSession, role_id: int) -> List[int]:
        """获取角色的菜单ID列表"""
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        )
        return [row[0] for row in result.all()]

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        sort: int = 0,
        data_scope: int = 1,
        data_scope_dept_ids: str = None,
        remark: str = None,
    ) -> int:
        """创建角色"""
        # 检查编码是否已存在
        existing = await RoleService.get_by_code(db, code)
        if existing:
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="角色编码已存在")

        role = Role(
            name=name,
            code=code,
            sort=sort,
            data_scope=data_scope,
            data_scope_dept_ids=data_scope_dept_ids,
            remark=remark,
        )
        db.add(role)
        await db.flush()
        await db.refresh(role)
        return role.id

    @staticmethod
    async def update(
        db: AsyncSession,
        role_id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        sort: Optional[int] = None,
        data_scope: Optional[int] = None,
        data_scope_dept_ids: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> bool:
        """更新角色"""
        role = await RoleService.get_by_id(db, role_id)
        if not role:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="角色不存在")

        if code is not None:
            # 检查新编码是否已存在
            existing = await RoleService.get_by_code(db, code)
            if existing and existing.id != role_id:
                raise BusinessException(code=ErrorCode.DATA_EXISTS, message="角色编码已存在")
            role.code = code

        if name is not None:
            role.name = name
        if sort is not None:
            role.sort = sort
        if data_scope is not None:
            role.data_scope = data_scope
        if data_scope_dept_ids is not None:
            role.data_scope_dept_ids = data_scope_dept_ids
        if remark is not None:
            role.remark = remark

        await db.flush()
        return True

    @staticmethod
    async def delete(db: AsyncSession, role_id: int) -> bool:
        """删除角色（软删除）"""
        role = await RoleService.get_by_id(db, role_id)
        if not role:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="角色不存在")

        # 检查是否是系统内置角色
        if role.type == 1:
            raise BusinessException(code=ErrorCode.PERMISSION_DENIED, message="不能删除系统内置角色")

        role.deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def delete_list(db: AsyncSession, role_ids: List[int]) -> int:
        """批量删除角色（软删除）"""
        count = 0
        for role_id in role_ids:
            try:
                await RoleService.delete(db, role_id)
                count += 1
            except BusinessException:
                pass
        return count