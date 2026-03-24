"""
部门服务
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.dept import Dept, DeptTree
from app.core.exceptions import BusinessException, ErrorCode


class DeptService:
    """部门服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, dept_id: int) -> Optional[Dept]:
        """根据ID获取部门"""
        result = await db.execute(
            select(Dept).where(Dept.id == dept_id, Dept.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, name: str = None, status: int = None) -> List[Dept]:
        """获取所有部门"""
        query = select(Dept).where(Dept.deleted == 0)
        if name:
            query = query.where(Dept.name.like(f"%{name}%"))
        if status is not None:
            query = query.where(Dept.status == status)
        query = query.order_by(Dept.sort.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_children_ids(db: AsyncSession, dept_id: int) -> List[int]:
        """获取部门及其所有子部门ID"""
        depts = await DeptService.get_all(db)
        return DeptService._get_children_ids(depts, dept_id)

    @staticmethod
    def _get_children_ids(depts: List[Dept], parent_id: int) -> List[int]:
        """递归获取子部门ID"""
        result = [parent_id]
        for dept in depts:
            if dept.parent_id == parent_id:
                result.extend(DeptService._get_children_ids(depts, dept.id))
        return result

    @staticmethod
    async def get_dept_tree(db: AsyncSession, name: str = None, status: int = None) -> List[dict]:
        """获取部门树"""
        depts = await DeptService.get_all(db, name, status)
        return DeptService._build_tree(depts, 0)

    @staticmethod
    def _build_tree(depts: List[Dept], parent_id: int) -> List[dict]:
        """构建部门树"""
        result = []
        for dept in depts:
            if dept.parent_id == parent_id:
                dept_dict = {
                    "id": dept.id,
                    "name": dept.name,
                    "parentId": dept.parent_id,
                    "sort": dept.sort,
                    "leaderUserId": dept.leader_user_id,
                    "phone": dept.phone,
                    "email": dept.email,
                    "status": dept.status,
                }
                children = DeptService._build_tree(depts, dept.id)
                if children:
                    dept_dict["children"] = children
                result.append(dept_dict)
        return result

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        parent_id: int,
        sort: int,
        leader_user_id: Optional[int],
        phone: Optional[str],
        email: Optional[str],
        status: int,
    ) -> int:
        """创建部门"""
        # 检查父部门是否存在
        if parent_id != 0:
            parent = await DeptService.get_by_id(db, parent_id)
            if not parent:
                raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="父部门不存在")

        # 检查同级部门名称是否重复
        result = await db.execute(
            select(Dept).where(
                Dept.name == name,
                Dept.parent_id == parent_id,
                Dept.deleted == 0,
            )
        )
        if result.scalar_one_or_none():
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="已存在该部门名称")

        # 创建部门
        dept = Dept(
            name=name,
            parent_id=parent_id,
            sort=sort,
            leader_user_id=leader_user_id,
            phone=phone,
            email=email,
            status=status,
        )
        db.add(dept)
        await db.commit()
        await db.refresh(dept)
        return dept.id

    @staticmethod
    async def update(
        db: AsyncSession,
        dept_id: int,
        name: str,
        parent_id: int,
        sort: int,
        leader_user_id: Optional[int],
        phone: Optional[str],
        email: Optional[str],
        status: int,
    ) -> None:
        """更新部门"""
        # 获取部门
        dept = await DeptService.get_by_id(db, dept_id)
        if not dept:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="部门不存在")

        # 检查父部门是否存在
        if parent_id != 0:
            parent = await DeptService.get_by_id(db, parent_id)
            if not parent:
                raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="父部门不存在")
            # 不能把自己设为自己的子部门
            if parent_id == dept_id:
                raise BusinessException(code=ErrorCode.BAD_REQUEST, message="不能将部门设为自己的子部门")

        # 检查同级部门名称是否重复（排除自己）
        result = await db.execute(
            select(Dept).where(
                Dept.name == name,
                Dept.parent_id == parent_id,
                Dept.id != dept_id,
                Dept.deleted == 0,
            )
        )
        if result.scalar_one_or_none():
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="已存在该部门名称")

        # 更新部门
        dept.name = name
        dept.parent_id = parent_id
        dept.sort = sort
        dept.leader_user_id = leader_user_id
        dept.phone = phone
        dept.email = email
        dept.status = status
        await db.commit()

    @staticmethod
    async def delete(db: AsyncSession, dept_id: int) -> None:
        """删除部门"""
        # 获取部门
        dept = await DeptService.get_by_id(db, dept_id)
        if not dept:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="部门不存在")

        # 检查是否有子部门
        result = await db.execute(
            select(Dept).where(Dept.parent_id == dept_id, Dept.deleted == 0).limit(1)
        )
        if result.scalar_one_or_none():
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="存在子部门，无法删除")

        # 软删除
        dept.deleted = 1
        await db.commit()