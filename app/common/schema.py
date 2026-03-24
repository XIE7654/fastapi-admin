"""
Schema 基础模块
提供统一的驼峰命名配置
"""
from typing import Any
from pydantic import BaseModel, AliasGenerator, ConfigDict


def to_camel(string: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# 统一的模型配置
CAMEL_CONFIG = ConfigDict(
    populate_by_name=True,  # 允许通过字段名或别名访问
    from_attributes=False,  # 默认不从 ORM 模型转换
)


def get_camel_alias_generator():
    """获取驼峰别名生成器"""
    return AliasGenerator(
        serialization_alias=to_camel,  # 序列化时使用驼峰
        validation_alias=to_camel,     # 反序列化时接受驼峰
    )


class CamelModel(BaseModel):
    """
    驼峰命名基础模型
    所有需要驼峰命名的 Schema 都应该继承此类
    """
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
            validation_alias=to_camel,
        ),
    )


class CamelORMModel(BaseModel):
    """
    驼峰命名 ORM 模型
    用于从 ORM 模型转换的 Schema
    """
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
            validation_alias=to_camel,
        ),
    )