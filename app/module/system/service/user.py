"""
用户服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.module.system.model.user import User, UserRole
from app.module.system.schema.user import UserCreate, UserUpdate, UserPageQuery
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BusinessException, ErrorCode
from app.common.utils import generate_snowflake_id


class UserService:
    """用户服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).where(User.username == username, User.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_mobile(db: AsyncSession, mobile: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await db.execute(
            select(User).where(User.mobile == mobile, User.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: UserPageQuery) -> Tuple[List[User], int]:
        """分页查询用户列表"""
        # 构建查询条件
        conditions = [User.deleted == 0]

        if query.username:
            conditions.append(User.username.like(f"%{query.username}%"))
        if query.nickname:
            conditions.append(User.nickname.like(f"%{query.nickname}%"))
        if query.mobile:
            conditions.append(User.mobile.like(f"%{query.mobile}%"))
        if query.status is not None:
            conditions.append(User.status == query.status)
        if query.dept_id:
            conditions.append(User.dept_id == query.dept_id)

        # 查询总数
        count_query = select(func.count()).select_from(User).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(User)
            .where(and_(*conditions))
            .order_by(User.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否存在
        existing = await UserService.get_by_username(db, user_create.username)
        if existing:
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="用户账号已存在")

        # 检查手机号是否存在
        if user_create.mobile:
            existing = await UserService.get_by_mobile(db, user_create.mobile)
            if existing:
                raise BusinessException(code=ErrorCode.DATA_EXISTS, message="手机号已存在")

        # 创建用户
        user = User(
            username=user_create.username,
            password=get_password_hash(user_create.password),
            nickname=user_create.nickname,
            email=user_create.email,
            mobile=user_create.mobile,
            gender=user_create.gender or 0,
            dept_id=user_create.dept_id,
            post_ids=",".join(str(pid) for pid in user_create.post_ids) if user_create.post_ids else None,
            status=user_create.status or 0,
            remark=user_create.remark,
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        return user

    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User:
        """更新用户"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        # 更新字段
        update_data = user_update.model_dump(exclude_unset=True)

        # 处理 gender -> sex 字段映射
        if "gender" in update_data:
            update_data["sex"] = update_data.pop("gender")

        # 处理岗位ID列表：将列表转为逗号分隔的字符串
        if "post_ids" in update_data:
            if update_data["post_ids"]:
                update_data["post_ids"] = ",".join(str(pid) for pid in update_data["post_ids"])
            else:
                # 空列表转为 None
                update_data["post_ids"] = None

        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await db.flush()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        if user.is_admin:
            raise BusinessException(code=ErrorCode.PERMISSION_DENIED, message="不能删除管理员用户")

        user.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def delete_list(db: AsyncSession, user_ids: List[int]) -> int:
        """批量删除用户（软删除）"""
        count = 0
        for user_id in user_ids:
            try:
                await UserService.delete(db, user_id)
                count += 1
            except BusinessException:
                pass
        return count

    @staticmethod
    async def get_enabled_users(db: AsyncSession) -> List[User]:
        """获取所有启用的用户"""
        result = await db.execute(
            select(User)
            .where(User.deleted == 0, User.status == 0)
            .order_by(User.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_password(
        db: AsyncSession,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """修改密码"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        # 验证旧密码
        if not verify_password(old_password, user.password):
            raise BusinessException(code=ErrorCode.USER_PASSWORD_INCORRECT, message="旧密码错误")

        # 更新密码
        user.password = get_password_hash(new_password)
        await db.flush()

        return True

    @staticmethod
    async def reset_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
        """重置密码"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        user.password = get_password_hash(new_password)
        await db.flush()

        return True

    @staticmethod
    async def update_status(db: AsyncSession, user_id: int, status: int) -> bool:
        """更新用户状态"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        if user.is_admin:
            raise BusinessException(code=ErrorCode.PERMISSION_DENIED, message="不能禁用管理员用户")

        user.status = status
        await db.flush()

        return True

    @staticmethod
    async def assign_roles(db: AsyncSession, user_id: int, role_ids: List[int]) -> bool:
        """分配用户角色"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="用户不存在")

        # 删除旧的角色关联
        await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        # TODO: 实现删除操作

        # 创建新的角色关联
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)

        await db.flush()

        return True

    @staticmethod
    async def validate_login(db: AsyncSession, username: str, password: str) -> User:
        """验证登录"""
        user = await UserService.get_by_username(db, username)

        if not user:
            raise BusinessException(code=ErrorCode.USER_NOT_EXISTS, message="用户不存在")

        if not verify_password(password, user.password):
            raise BusinessException(code=ErrorCode.USER_PASSWORD_INCORRECT, message="密码错误")

        if user.status != 0:
            raise BusinessException(code=ErrorCode.USER_DISABLED, message="用户已被禁用")

        return user