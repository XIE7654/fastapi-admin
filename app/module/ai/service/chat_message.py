"""
AI 聊天消息服务
参考 ruoyi-vue-pro yudao-module-ai AiChatMessageService
"""
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Tuple, AsyncGenerator, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.chat_message import ChatMessage
from app.module.ai.schema.chat_message import ChatMessagePageQuery, ChatMessageSendReqVO, ChatMessageSendRespVO
from app.core.exceptions import BusinessException


class ChatMessageService:
    """AI 聊天消息服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
        """根据ID获取消息"""
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list_by_conversation_id(
        db: AsyncSession,
        conversation_id: int
    ) -> List[ChatMessage]:
        """根据对话ID获取消息列表"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id, ChatMessage.deleted == 0)
            .order_by(ChatMessage.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        query: ChatMessagePageQuery
    ) -> Tuple[List[ChatMessage], int]:
        """分页查询消息列表"""
        # 构建查询条件
        conditions = [ChatMessage.deleted == 0]

        if query.conversation_id:
            conditions.append(ChatMessage.conversation_id == query.conversation_id)
        if query.user_id:
            conditions.append(ChatMessage.user_id == query.user_id)
        if query.content:
            conditions.append(ChatMessage.content.like(f"%{query.content}%"))
        if query.create_time and len(query.create_time) == 2:
            conditions.append(ChatMessage.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        count_query = select(func.count()).select_from(ChatMessage).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(ChatMessage)
            .where(and_(*conditions))
            .order_by(ChatMessage.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        messages = result.scalars().all()

        return list(messages), total

    @staticmethod
    async def delete(db: AsyncSession, message_id: int) -> bool:
        """删除消息（软删除）"""
        message = await ChatMessageService.get_by_id(db, message_id)
        if not message:
            raise BusinessException(code=404, message="消息不存在")

        message.deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def delete_by_conversation_id(
        db: AsyncSession,
        conversation_id: int
    ) -> bool:
        """删除指定对话的所有消息"""
        result = await db.execute(
            select(ChatMessage).where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.deleted == 0
            )
        )
        messages = result.scalars().all()

        for message in messages:
            message.deleted = 1

        await db.flush()
        return True

    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        content: str,
        message_type: str = "user",
        model: Optional[str] = None,
        model_id: Optional[int] = None,
        segment_ids: Optional[List[int]] = None,
        web_search_pages: Optional[List[dict]] = None,
        attachment_urls: Optional[List[str]] = None,
        reasoning_content: Optional[str] = None,
        use_context: bool = True,
    ) -> ChatMessage:
        """创建消息"""
        message = ChatMessage(
            conversation_id=conversation_id,
            user_id=user_id,
            type=message_type,
            content=content,
            model=model,
            model_id=model_id,
            segment_ids=segment_ids,
            web_search_pages=web_search_pages,
            attachment_urls=attachment_urls,
            reasoning_content=reasoning_content,
            use_context=use_context,
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def send_message(
        db: AsyncSession,
        send_req: ChatMessageSendReqVO,
        user_id: int
    ) -> ChatMessageSendRespVO:
        """发送消息（段式）"""
        # 1. 创建用户消息
        user_message = await ChatMessageService.create_message(
            db=db,
            conversation_id=send_req.conversation_id,
            user_id=user_id,
            content=send_req.content,
            message_type="user",
            attachment_urls=send_req.attachment_urls,
            use_context=send_req.use_context or True,
        )

        # 2. 创建AI响应消息（这里需要集成实际的AI服务）
        # 目前先返回模拟响应
        ai_message = await ChatMessageService.create_message(
            db=db,
            conversation_id=send_req.conversation_id,
            user_id=user_id,
            content="这是一个模拟的AI响应，请集成实际的AI服务。",
            message_type="assistant",
            use_context=send_req.use_context or True,
        )

        # 3. 构建响应
        return ChatMessageSendRespVO(
            send=ChatMessageSendRespVO.Message(
                id=user_message.id,
                type=user_message.type,
                content=user_message.content,
                create_time=user_message.create_time,
            ),
            receive=ChatMessageSendRespVO.Message(
                id=ai_message.id,
                type=ai_message.type,
                content=ai_message.content,
                create_time=ai_message.create_time,
            ),
        )

    @staticmethod
    async def send_message_stream(
        db: AsyncSession,
        send_req: ChatMessageSendReqVO,
        user_id: int
    ) -> AsyncGenerator[str, None]:
        """发送消息（流式）"""
        # 1. 创建用户消息
        user_message = await ChatMessageService.create_message(
            db=db,
            conversation_id=send_req.conversation_id,
            user_id=user_id,
            content=send_req.content,
            message_type="user",
            attachment_urls=send_req.attachment_urls,
            use_context=send_req.use_context or True,
        )

        # 2. 先发送用户消息
        send_resp = {
            "send": {
                "id": user_message.id,
                "type": user_message.type,
                "content": user_message.content,
                "createTime": user_message.create_time.isoformat() if user_message.create_time else None,
            },
            "receive": None,
        }
        yield f"data: {json.dumps(send_resp, ensure_ascii=False)}\n\n"

        # 3. 模拟流式响应（实际需要集成AI服务）
        # 这里模拟一个简单的流式响应
        response_text = "这是一个模拟的AI流式响应。请集成实际的AI服务来获得真实的对话体验。"
        full_content = ""
        ai_message_id = None

        for char in response_text:
            full_content += char
            receive_resp = {
                "send": None,
                "receive": {
                    "id": None,
                    "type": "assistant",
                    "content": full_content,
                    "createTime": datetime.now().isoformat(),
                },
            }
            yield f"data: {json.dumps(receive_resp, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)  # 模拟打字延迟

        # 4. 创建AI消息记录
        ai_message = await ChatMessageService.create_message(
            db=db,
            conversation_id=send_req.conversation_id,
            user_id=user_id,
            content=full_content,
            message_type="assistant",
            use_context=send_req.use_context or True,
        )

        # 5. 发送最终响应
        final_resp = {
            "send": None,
            "receive": {
                "id": ai_message.id,
                "type": "assistant",
                "content": full_content,
                "createTime": ai_message.create_time.isoformat() if ai_message.create_time else None,
            },
        }
        yield f"data: {json.dumps(final_resp, ensure_ascii=False)}\n\n"