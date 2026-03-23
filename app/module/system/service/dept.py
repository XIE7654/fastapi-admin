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