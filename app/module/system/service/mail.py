"""
邮件服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.mail import MailAccount, MailTemplate, MailLog


class MailAccountService:
    """邮箱账号服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, account_id: int) -> Optional[MailAccount]:
        """根据ID获取邮箱账号"""
        result = await db.execute(
            select(MailAccount).where(MailAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[MailAccount]:
        """获取所有邮箱账号"""
        result = await db.execute(
            select(MailAccount).order_by(MailAccount.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        mail: str = None,
        username: str = None,
    ) -> Tuple[List[MailAccount], int]:
        """分页获取邮箱账号"""
        conditions = []

        if mail:
            conditions.append(MailAccount.mail.like(f"%{mail}%"))
        if username:
            conditions.append(MailAccount.username.like(f"%{username}%"))

        # 查询总数
        count_query = select(func.count(MailAccount.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(MailAccount)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(MailAccount.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class MailTemplateService:
    """邮件模板服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int) -> Optional[MailTemplate]:
        """根据ID获取邮件模板"""
        result = await db.execute(
            select(MailTemplate).where(MailTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[MailTemplate]:
        """获取所有邮件模板"""
        result = await db.execute(
            select(MailTemplate).order_by(MailTemplate.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        code: str = None,
        account_id: int = None,
        status: int = None,
    ) -> Tuple[List[MailTemplate], int]:
        """分页获取邮件模板"""
        conditions = []

        if name:
            conditions.append(MailTemplate.name.like(f"%{name}%"))
        if code:
            conditions.append(MailTemplate.code.like(f"%{code}%"))
        if account_id is not None:
            conditions.append(MailTemplate.account_id == account_id)
        if status is not None:
            conditions.append(MailTemplate.status == status)

        # 查询总数
        count_query = select(func.count(MailTemplate.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(MailTemplate)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(MailTemplate.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class MailLogService:
    """邮件日志服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[MailLog]:
        """根据ID获取邮件日志"""
        result = await db.execute(
            select(MailLog).where(MailLog.id == log_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        user_id: int = None,
        user_type: int = None,
        to_mails: str = None,
        account_id: int = None,
        template_id: int = None,
        send_status: int = None,
        send_time: list = None,
    ) -> Tuple[List[MailLog], int]:
        """分页获取邮件日志"""
        conditions = []

        if user_id is not None:
            conditions.append(MailLog.user_id == user_id)
        if user_type is not None:
            conditions.append(MailLog.user_type == user_type)
        if to_mails:
            conditions.append(MailLog.to_mails.like(f"%{to_mails}%"))
        if account_id is not None:
            conditions.append(MailLog.account_id == account_id)
        if template_id is not None:
            conditions.append(MailLog.template_id == template_id)
        if send_status is not None:
            conditions.append(MailLog.send_status == send_status)
        if send_time and len(send_time) == 2:
            conditions.append(MailLog.send_time.between(send_time[0], send_time[1]))

        # 查询总数
        count_query = select(func.count(MailLog.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(MailLog)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(MailLog.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total