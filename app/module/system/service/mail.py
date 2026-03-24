"""
邮件服务
"""
import re
from typing import Optional, List, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.mail import MailAccount, MailTemplate, MailLog
from app.core.exceptions import BusinessException, ErrorCode


# 正则表达式，匹配 {} 中的变量
PATTERN_PARAMS = re.compile(r'\{(.*?)}')


class MailAccountService:
    """邮箱账号服务"""

    @staticmethod
    async def create(
        db: AsyncSession,
        mail: str,
        username: str,
        password: str,
        host: str,
        port: int,
        ssl_enable: bool = False,
        starttls_enable: bool = False,
    ) -> MailAccount:
        """创建邮箱账号"""
        account = MailAccount(
            mail=mail,
            username=username,
            password=password,
            host=host,
            port=port,
            ssl_enable=1 if ssl_enable else 0,
            starttls_enable=1 if starttls_enable else 0,
        )
        db.add(account)
        await db.flush()
        return account

    @staticmethod
    async def update(
        db: AsyncSession,
        account_id: int,
        mail: str = None,
        username: str = None,
        password: str = None,
        host: str = None,
        port: int = None,
        ssl_enable: bool = None,
        starttls_enable: bool = None,
    ) -> Optional[MailAccount]:
        """更新邮箱账号"""
        account = await MailAccountService.get_by_id(db, account_id)
        if not account:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="邮箱账号不存在")

        if mail is not None:
            account.mail = mail
        if username is not None:
            account.username = username
        if password is not None:
            account.password = password
        if host is not None:
            account.host = host
        if port is not None:
            account.port = port
        if ssl_enable is not None:
            account.ssl_enable = 1 if ssl_enable else 0
        if starttls_enable is not None:
            account.starttls_enable = 1 if starttls_enable else 0

        await db.flush()
        return account

    @staticmethod
    async def delete(db: AsyncSession, account_id: int) -> bool:
        """删除邮箱账号"""
        account = await MailAccountService.get_by_id(db, account_id)
        if not account:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="邮箱账号不存在")

        # 检查是否有关联的邮件模板
        result = await db.execute(
            select(func.count(MailTemplate.id)).where(MailTemplate.account_id == account_id)
        )
        template_count = result.scalar() or 0
        if template_count > 0:
            raise BusinessException(code=ErrorCode.BAD_REQUEST, message="存在关联的邮件模板，无法删除")

        await db.delete(account)
        await db.flush()
        return True

    @staticmethod
    async def delete_by_ids(db: AsyncSession, account_ids: List[int]) -> int:
        """批量删除邮箱账号"""
        count = 0
        for account_id in account_ids:
            try:
                await MailAccountService.delete(db, account_id)
                count += 1
            except BusinessException:
                continue
        return count

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
    async def get_by_code(db: AsyncSession, code: str) -> Optional[MailTemplate]:
        """根据编码获取邮件模板"""
        result = await db.execute(
            select(MailTemplate).where(MailTemplate.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def parse_template_params(title: str, content: str) -> str:
        """解析标题和内容中的参数"""
        title_params = re.findall(PATTERN_PARAMS, title) if title else []
        content_params = re.findall(PATTERN_PARAMS, content) if content else []
        # 合并参数并去重
        all_params = list(dict.fromkeys(title_params + content_params))
        return ','.join(all_params) if all_params else ''

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        account_id: int,
        title: str,
        content: str,
        status: int,
        nickname: str = None,
        remark: str = None,
    ) -> int:
        """创建邮件模板"""
        # 校验编码是否重复
        existing = await MailTemplateService.get_by_code(db, code)
        if existing:
            raise BusinessException(
                code=ErrorCode.MAIL_TEMPLATE_CODE_EXISTS,
                message=f"邮件模版 code({code}) 已存在"
            )

        # 解析模板参数
        params = MailTemplateService.parse_template_params(title, content)

        # 创建模板
        template = MailTemplate(
            name=name,
            code=code,
            account_id=account_id,
            nickname=nickname,
            title=title,
            content=content,
            params=params,
            status=status,
            remark=remark,
        )
        db.add(template)
        await db.flush()
        await db.refresh(template)
        return template.id

    @staticmethod
    async def update(
        db: AsyncSession,
        template_id: int,
        name: str = None,
        code: str = None,
        account_id: int = None,
        title: str = None,
        content: str = None,
        status: int = None,
        nickname: str = None,
        remark: str = None,
    ) -> bool:
        """更新邮件模板"""
        # 校验存在
        template = await MailTemplateService.get_by_id(db, template_id)
        if not template:
            raise BusinessException(
                code=ErrorCode.MAIL_TEMPLATE_NOT_EXISTS,
                message="邮件模版不存在"
            )

        # 校验编码是否重复
        if code is not None:
            existing = await MailTemplateService.get_by_code(db, code)
            if existing and existing.id != template_id:
                raise BusinessException(
                    code=ErrorCode.MAIL_TEMPLATE_CODE_EXISTS,
                    message=f"邮件模版 code({code}) 已存在"
                )

        # 更新字段
        need_parse_params = False
        if name is not None:
            template.name = name
        if code is not None:
            template.code = code
        if account_id is not None:
            template.account_id = account_id
        if title is not None:
            template.title = title
            need_parse_params = True
        if content is not None:
            template.content = content
            need_parse_params = True
        if status is not None:
            template.status = status
        if nickname is not None:
            template.nickname = nickname
        if remark is not None:
            template.remark = remark

        # 如果标题或内容有变化，重新解析参数
        if need_parse_params:
            template.params = MailTemplateService.parse_template_params(
                template.title, template.content
            )

        await db.flush()
        return True

    @staticmethod
    async def delete(db: AsyncSession, template_id: int) -> bool:
        """删除邮件模板"""
        # 校验存在
        template = await MailTemplateService.get_by_id(db, template_id)
        if not template:
            raise BusinessException(
                code=ErrorCode.MAIL_TEMPLATE_NOT_EXISTS,
                message="邮件模版不存在"
            )

        await db.delete(template)
        await db.flush()
        return True

    @staticmethod
    async def delete_list(db: AsyncSession, template_ids: List[int]) -> int:
        """批量删除邮件模板"""
        count = 0
        for template_id in template_ids:
            try:
                await MailTemplateService.delete(db, template_id)
                count += 1
            except BusinessException:
                pass
        return count

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
        create_time: list = None,
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
        if create_time and len(create_time) == 2:
            conditions.append(MailTemplate.create_time.between(create_time[0], create_time[1]))

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