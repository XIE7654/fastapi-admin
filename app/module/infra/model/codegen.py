"""
代码生成模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text, Boolean

from app.module.infra.model.base import Base, TimestampMixin


class CodegenTable(Base, TimestampMixin):
    """代码生成表定义"""

    __tablename__ = "infra_codegen_table"

    data_source_config_id = Column(BigInteger, nullable=False, comment="数据源配置的编号")
    scene = Column(SmallInteger, nullable=False, default=1, comment="生成场景")
    table_name = Column(String(200), nullable=False, default="", comment="表名称")
    table_comment = Column(String(500), nullable=False, default="", comment="表描述")
    remark = Column(String(500), nullable=True, comment="备注")
    module_name = Column(String(30), nullable=False, comment="模块名")
    business_name = Column(String(30), nullable=False, comment="业务名")
    class_name = Column(String(100), nullable=False, default="", comment="类名称")
    class_comment = Column(String(50), nullable=False, comment="类描述")
    author = Column(String(50), nullable=False, comment="作者")
    template_type = Column(SmallInteger, nullable=False, default=1, comment="模板类型")
    front_type = Column(SmallInteger, nullable=False, comment="前端类型")
    parent_menu_id = Column(BigInteger, nullable=True, comment="父菜单编号")
    master_table_id = Column(BigInteger, nullable=True, comment="主表的编号")
    sub_join_column_id = Column(BigInteger, nullable=True, comment="子表关联主表的字段编号")
    sub_join_many = Column(SmallInteger, nullable=True, comment="主表与子表是否一对多")
    tree_parent_column_id = Column(BigInteger, nullable=True, comment="树表的父字段编号")
    tree_name_column_id = Column(BigInteger, nullable=True, comment="树表的名字字段编号")


class CodegenColumn(Base, TimestampMixin):
    """代码生成表字段定义"""

    __tablename__ = "infra_codegen_column"

    table_id = Column(BigInteger, nullable=False, comment="表编号")
    column_name = Column(String(200), nullable=False, comment="字段名")
    data_type = Column(String(100), nullable=False, comment="字段类型")
    column_comment = Column(String(500), nullable=False, comment="字段描述")
    nullable = Column(SmallInteger, nullable=False, comment="是否允许为空")
    primary_key = Column(SmallInteger, nullable=False, comment="是否主键")
    ordinal_position = Column(Integer, nullable=False, comment="排序")
    java_type = Column(String(32), nullable=False, comment="Java属性类型")
    java_field = Column(String(64), nullable=False, comment="Java属性名")
    dict_type = Column(String(200), nullable=True, default="", comment="字典类型")
    example = Column(String(64), nullable=True, comment="数据示例")
    create_operation = Column(SmallInteger, nullable=False, comment="是否为Create创建操作的字段")
    update_operation = Column(SmallInteger, nullable=False, comment="是否为Update更新操作的字段")
    list_operation = Column(SmallInteger, nullable=False, comment="是否为List查询操作的字段")
    list_operation_condition = Column(String(32), nullable=False, default="=", comment="List查询操作的条件类型")
    list_operation_result = Column(SmallInteger, nullable=False, comment="是否为List查询操作的返回字段")
    html_type = Column(String(32), nullable=False, comment="显示类型")