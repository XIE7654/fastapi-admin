"""
AI 聊天角色服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiChatRoleService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.chat_role import ChatRole
from app.module.ai.schema.chat_role import (
    ChatRoleCreate,
    ChatRoleUpdate,
    ChatRolePageQuery,
)
from app.core.exceptions import BusinessException


class ChatRoleErrorCode:
    """聊天角色错误码定义"""

    CHAT_ROLE_NOT_EXISTS = 1040020000
    CHAT_ROLE_DISABLE = 1040020001


class ChatRoleService:
    """AI 聊天角色服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Optional[ChatRole]:
        """根据ID获取聊天角色"""
        result = await db.execute(
            select(ChatRole).where(ChatRole.id == role_id, ChatRole.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: ChatRolePageQuery) -> Tuple[List[ChatRole], int]:
        """分页查询聊天角色列表"""
        # 构建查询条件
        conditions = [ChatRole.deleted == 0]

        if query.name:
            conditions.append(ChatRole.name.like(f"%{query.name}%"))
        if query.category:
            conditions.append(ChatRole.category.like(f"%{query.category}%"))
        if query.public_status is not None:
            # public_status 是布尔值，转换为数据库的 SmallInteger (0/1)
            conditions.append(ChatRole.public_status == (1 if query.public_status else 0))

        # 查询总数
        count_query = select(func.count()).select_from(ChatRole).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(ChatRole)
            .where(and_(*conditions))
            .order_by(ChatRole.sort.asc(), ChatRole.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        roles = result.scalars().all()

        return list(roles), total

    @staticmethod
    async def create(db: AsyncSession, role_create: ChatRoleCreate) -> ChatRole:
        """创建聊天角色"""
        role = ChatRole(
            user_id=role_create.user_id,
            model_id=role_create.model_id,
            name=role_create.name,
            avatar=role_create.avatar,
            category=role_create.category,
            sort=role_create.sort or 0,
            description=role_create.description,
            system_message=role_create.system_message,
            knowledge_ids=role_create.knowledge_ids,
            tool_ids=role_create.tool_ids,
            mcp_client_names=role_create.mcp_client_names,
            public_status=role_create.public_status or 0,
            status=role_create.status or 0,
        )

        db.add(role)
        await db.flush()
        await db.refresh(role)

        return role

    @staticmethod
    async def update(db: AsyncSession, role_id: int, role_update: ChatRoleUpdate) -> ChatRole:
        """更新聊天角色"""
        role = await ChatRoleService.get_by_id(db, role_id)
        if not role:
            raise BusinessException(
                code=ChatRoleErrorCode.CHAT_ROLE_NOT_EXISTS,
                message="聊天角色不存在"
            )

        # 更新字段
        update_data = role_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(role, key):
                setattr(role, key, value)

        await db.flush()
        await db.refresh(role)

        return role

    @staticmethod
    async def delete(db: AsyncSession, role_id: int) -> bool:
        """删除聊天角色（软删除）"""
        role = await ChatRoleService.get_by_id(db, role_id)
        if not role:
            raise BusinessException(
                code=ChatRoleErrorCode.CHAT_ROLE_NOT_EXISTS,
                message="聊天角色不存在"
            )

        role.deleted = 1
        await db.flush()

        return True