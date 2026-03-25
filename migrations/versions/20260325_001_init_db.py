"""初始化数据库表结构和数据

Revision ID: 001
Revises:
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库"""
    # 获取SQL文件路径
    import os
    sql_file = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'fastadmin.sql')

    # 读取SQL文件
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 分割SQL语句并执行
    # 注意：这里使用原生SQL执行，跳过外键检查
    connection = op.get_bind()

    # 禁用外键检查
    connection.execute(sa.text('SET FOREIGN_KEY_CHECKS = 0'))

    # 分割并执行SQL语句
    statements = sql_content.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--') and not statement.startswith('/*'):
            try:
                connection.execute(sa.text(statement))
            except Exception as e:
                # 忽略某些特定错误
                print(f"Warning: {e}")

    # 启用外键检查
    connection.execute(sa.text('SET FOREIGN_KEY_CHECKS = 1'))


def downgrade() -> None:
    """降级数据库 - 删除所有表"""
    connection = op.get_bind()

    # 禁用外键检查
    connection.execute(sa.text('SET FOREIGN_KEY_CHECKS = 0'))

    # 获取所有表名
    result = connection.execute(sa.text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
    ))
    tables = [row[0] for row in result.fetchall()]

    # 删除所有表
    for table in tables:
        connection.execute(sa.text(f'DROP TABLE IF EXISTS `{table}`'))

    # 启用外键检查
    connection.execute(sa.text('SET FOREIGN_KEY_CHECKS = 1'))