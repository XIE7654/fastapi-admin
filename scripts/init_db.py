"""
数据库初始化脚本
创建必要的表结构和管理员账号
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.security import get_password_hash
from app.core.database import Base

# 导入所有模型
from app.module.system.model import *


async def init_database():
    """初始化数据库"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("数据库表创建完成！")


async def create_admin_user():
    """创建管理员账号"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # 检查是否已存在admin用户
        result = await session.execute(
            text("SELECT id FROM system_user WHERE username = 'admin'")
        )
        if result.fetchone():
            print("管理员账号已存在")
            return

        # 创建管理员
        await session.execute(
            text("""
                INSERT INTO system_user
                (username, password, nickname, gender, status, dept_id, tenant_id, deleted)
                VALUES
                ('admin', :password, '超级管理员', 1, 0, 1, 1, 0)
            """),
            {"password": get_password_hash("admin123")}
        )

        # 创建默认部门
        await session.execute(
            text("""
                INSERT INTO system_dept
                (name, parent_id, sort, status, tenant_id, deleted)
                VALUES
                ('芋道科技', 0, 0, 0, 1, 0)
            """)
        )

        # 创建默认角色
        await session.execute(
            text("""
                INSERT INTO system_role
                (name, code, sort, data_scope, status, type, tenant_id, deleted)
                VALUES
                ('超级管理员', 'super_admin', 0, 1, 0, 1, 1, 0)
            """)
        )

        await session.commit()
        print("管理员账号创建成功！用户名: admin, 密码: admin123")


async def create_tenant():
    """创建默认租户"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # 检查是否已存在租户
        result = await session.execute(
            text("SELECT id FROM system_tenant WHERE id = 1")
        )
        if result.fetchone():
            print("默认租户已存在")
            return

        await session.execute(
            text("""
                INSERT INTO system_tenant
                (id, name, contact_name, contact_mobile, status, package_id, deleted)
                VALUES
                (1, '芋道科技', '管理员', '13800138000', 0, NULL, 0)
            """)
        )

        await session.commit()
        print("默认租户创建成功！")


async def main():
    """主函数"""
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)

    try:
        await init_database()
        await create_tenant()
        await create_admin_user()
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
    except Exception as e:
        print(f"初始化失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())