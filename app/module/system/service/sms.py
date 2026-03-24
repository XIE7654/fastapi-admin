"""
短信渠道服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.sms import SmsChannel, SmsTemplate
from app.core.exceptions import BusinessException, ErrorCode


class SmsChannelService:
    """短信渠道服务"""

    @staticmethod
    async def create(
        db: AsyncSession,
        signature: str,
        code: str,
        status: int,
        api_key: str,
        remark: str = None,
        api_secret: str = None,
        callback_url: str = None,
    ) -> SmsChannel:
        """创建短信渠道"""
        channel = SmsChannel(
            signature=signature,
            code=code,
            status=status,
            remark=remark,
            api_key=api_key,
            api_secret=api_secret,
            callback_url=callback_url,
        )
        db.add(channel)
        await db.flush()
        return channel

    @staticmethod
    async def update(
        db: AsyncSession,
        channel_id: int,
        signature: str = None,
        code: str = None,
        status: int = None,
        api_key: str = None,
        remark: str = None,
        api_secret: str = None,
        callback_url: str = None,
    ) -> Optional[SmsChannel]:
        """更新短信渠道"""
        channel = await SmsChannelService.get_by_id(db, channel_id)
        if not channel:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="短信渠道不存在")

        if signature is not None:
            channel.signature = signature
        if code is not None:
            channel.code = code
        if status is not None:
            channel.status = status
        if api_key is not None:
            channel.api_key = api_key
        if remark is not None:
            channel.remark = remark
        if api_secret is not None:
            channel.api_secret = api_secret
        if callback_url is not None:
            channel.callback_url = callback_url

        await db.flush()
        return channel

    @staticmethod
    async def delete(db: AsyncSession, channel_id: int) -> bool:
        """删除短信渠道"""
        channel = await SmsChannelService.get_by_id(db, channel_id)
        if not channel:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="短信渠道不存在")

        # 检查是否有关联的短信模板
        result = await db.execute(
            select(func.count(SmsTemplate.id)).where(SmsTemplate.channel_id == channel_id)
        )
        template_count = result.scalar() or 0
        if template_count > 0:
            raise BusinessException(code=ErrorCode.BAD_REQUEST, message="存在关联的短信模板，无法删除")

        await db.delete(channel)
        await db.flush()
        return True

    @staticmethod
    async def delete_by_ids(db: AsyncSession, channel_ids: List[int]) -> int:
        """批量删除短信渠道"""
        count = 0
        for channel_id in channel_ids:
            try:
                await SmsChannelService.delete(db, channel_id)
                count += 1
            except BusinessException:
                continue
        return count

    @staticmethod
    async def get_template_count_by_channel_id(db: AsyncSession, channel_id: int) -> int:
        """获取渠道关联的模板数量"""
        result = await db.execute(
            select(func.count(SmsTemplate.id)).where(SmsTemplate.channel_id == channel_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_by_id(db: AsyncSession, channel_id: int) -> Optional[SmsChannel]:
        """根据ID获取短信渠道"""
        result = await db.execute(
            select(SmsChannel).where(SmsChannel.id == channel_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SmsChannel]:
        """获取所有短信渠道"""
        result = await db.execute(
            select(SmsChannel).order_by(SmsChannel.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        status: int = None,
        signature: str = None,
        code: str = None,
    ) -> Tuple[List[SmsChannel], int]:
        """分页获取短信渠道"""
        conditions = []

        if status is not None:
            conditions.append(SmsChannel.status == status)
        if signature:
            conditions.append(SmsChannel.signature.like(f"%{signature}%"))
        if code:
            conditions.append(SmsChannel.code.like(f"%{code}%"))

        # 查询总数
        count_query = select(func.count(SmsChannel.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SmsChannel)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsChannel.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class SmsTemplateService:
    """短信模板服务"""

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        channel_id: int,
        content: str,
        status: int,
        remark: str = None,
    ) -> SmsTemplate:
        """创建短信模板"""
        import re

        # 获取渠道编码
        channel = await SmsChannelService.get_by_id(db, channel_id)
        if not channel:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="短信渠道不存在")

        # 解析模板参数
        params = re.findall(r'\{(.*?)}', content)
        params_str = ','.join(params) if params else ''

        template = SmsTemplate(
            name=name,
            code=code,
            channel_id=channel_id,
            channel_code=channel.code,
            content=content,
            params=params_str,
            status=status,
            remark=remark,
        )
        db.add(template)
        await db.flush()
        return template

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int) -> Optional[dict]:
        """根据ID获取短信模板"""
        from app.module.system.model.sms import SmsTemplate
        result = await db.execute(
            select(SmsTemplate).where(SmsTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        status: int = None,
        name: str = None,
        code: str = None,
        channel_id: int = None,
    ) -> Tuple[List, int]:
        """分页获取短信模板"""
        from app.module.system.model.sms import SmsTemplate

        conditions = []

        if status is not None:
            conditions.append(SmsTemplate.status == status)
        if name:
            conditions.append(SmsTemplate.name.like(f"%{name}%"))
        if code:
            conditions.append(SmsTemplate.code.like(f"%{code}%"))
        if channel_id is not None:
            conditions.append(SmsTemplate.channel_id == channel_id)

        # 查询总数
        count_query = select(func.count(SmsTemplate.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SmsTemplate)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsTemplate.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total