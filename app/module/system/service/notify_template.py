"""
站内信模板服务
"""
import re
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.notify import NotifyTemplate
from app.core.exceptions import BusinessException, ErrorCode


class NotifyTemplateService:
    """站内信模板服务"""

    # 正则表达式，匹配 {} 中的变量
    PATTERN_PARAMS = re.compile(r'\{(.*?)}')

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int) -> Optional[NotifyTemplate]:
        """根据ID获取站内信模板"""
        result = await db.execute(
            select(NotifyTemplate).where(NotifyTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[NotifyTemplate]:
        """根据编码获取站内信模板"""
        result = await db.execute(
            select(NotifyTemplate).where(NotifyTemplate.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def parse_template_content_params(content: str) -> str:
        """解析模板内容中的参数"""
        params = re.findall(NotifyTemplateService.PATTERN_PARAMS, content)
        return ','.join(params) if params else ''

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        type: int,
        nickname: str,
        content: str,
        status: int,
        remark: str = None,
    ) -> int:
        """创建站内信模板"""
        # 校验编码是否重复
        existing = await NotifyTemplateService.get_by_code(db, code)
        if existing:
            raise BusinessException(
                code=ErrorCode.NOTIFY_TEMPLATE_CODE_DUPLICATE,
                message=f"已经存在编码为【{code}】的站内信模板"
            )

        # 解析模板参数
        params = NotifyTemplateService.parse_template_content_params(content)

        # 创建模板
        template = NotifyTemplate(
            name=name,
            code=code,
            type=type,
            nickname=nickname,
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
        type: int = None,
        nickname: str = None,
        content: str = None,
        status: int = None,
        remark: str = None,
    ) -> bool:
        """更新站内信模板"""
        # 校验存在
        template = await NotifyTemplateService.get_by_id(db, template_id)
        if not template:
            raise BusinessException(
                code=ErrorCode.NOTIFY_TEMPLATE_NOT_EXISTS,
                message="站内信模版不存在"
            )

        # 校验编码是否重复
        if code is not None:
            existing = await NotifyTemplateService.get_by_code(db, code)
            if existing and existing.id != template_id:
                raise BusinessException(
                    code=ErrorCode.NOTIFY_TEMPLATE_CODE_DUPLICATE,
                    message=f"已经存在编码为【{code}】的站内信模板"
                )

        # 更新字段
        if name is not None:
            template.name = name
        if code is not None:
            template.code = code
        if type is not None:
            template.type = type
        if nickname is not None:
            template.nickname = nickname
        if content is not None:
            template.content = content
            template.params = NotifyTemplateService.parse_template_content_params(content)
        if status is not None:
            template.status = status
        if remark is not None:
            template.remark = remark

        await db.flush()
        return True

    @staticmethod
    async def delete(db: AsyncSession, template_id: int) -> bool:
        """删除站内信模板"""
        # 校验存在
        template = await NotifyTemplateService.get_by_id(db, template_id)
        if not template:
            raise BusinessException(
                code=ErrorCode.NOTIFY_TEMPLATE_NOT_EXISTS,
                message="站内信模版不存在"
            )

        await db.delete(template)
        await db.flush()
        return True

    @staticmethod
    async def delete_list(db: AsyncSession, template_ids: List[int]) -> int:
        """批量删除站内信模板"""
        count = 0
        for template_id in template_ids:
            try:
                await NotifyTemplateService.delete(db, template_id)
                count += 1
            except BusinessException:
                pass
        return count

    @staticmethod
    async def get_all(db: AsyncSession) -> List[NotifyTemplate]:
        """获取所有站内信模板"""
        result = await db.execute(
            select(NotifyTemplate).order_by(NotifyTemplate.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        code: str = None,
        status: int = None,
        type: int = None,
    ) -> Tuple[List[NotifyTemplate], int]:
        """分页获取站内信模板"""
        conditions = []

        if name:
            conditions.append(NotifyTemplate.name.like(f"%{name}%"))
        if code:
            conditions.append(NotifyTemplate.code.like(f"%{code}%"))
        if status is not None:
            conditions.append(NotifyTemplate.status == status)
        if type is not None:
            conditions.append(NotifyTemplate.type == type)

        # 查询总数
        count_query = select(func.count(NotifyTemplate.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(NotifyTemplate)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(NotifyTemplate.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class NotifyMessageServiceExt:
    """站内信消息扩展服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        user_id: int = None,
        user_type: int = None,
        read_status: int = None,
        template_code: str = None,
        template_type: int = None,
        create_time: list = None,
    ) -> Tuple[List, int]:
        """分页获取站内信消息"""
        from app.module.system.model.notify import NotifyMessage

        conditions = []

        if user_id is not None:
            conditions.append(NotifyMessage.user_id == user_id)
        if user_type is not None:
            conditions.append(NotifyMessage.user_type == user_type)
        if read_status is not None:
            conditions.append(NotifyMessage.read_status == read_status)
        if template_code:
            conditions.append(NotifyMessage.template_code.like(f"%{template_code}%"))
        if template_type is not None:
            conditions.append(NotifyMessage.template_type == template_type)
        if create_time and len(create_time) == 2:
            conditions.append(NotifyMessage.create_time.between(create_time[0], create_time[1]))

        # 查询总数
        count_query = select(func.count(NotifyMessage.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(NotifyMessage)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(NotifyMessage.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total