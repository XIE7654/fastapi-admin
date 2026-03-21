"""
安全认证模块
JWT Token 生成与验证，密码加密
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
import bcrypt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """生成密码哈希 (rounds=4, 与 ruoyi-vue-pro 的 BCryptPasswordEncoder 保持一致)"""
    salt = bcrypt.gensalt(rounds=4)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(
    subject: str,
    user_id: int,
    tenant_id: Optional[int] = None,
    additional_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    创建访问令牌

    Args:
        subject: 令牌主题（通常是用户名）
        user_id: 用户ID
        tenant_id: 租户ID
        additional_data: 额外数据

    Returns:
        JWT访问令牌
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    if additional_data:
        payload.update(additional_data)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    user_id: int,
    tenant_id: Optional[int] = None,
) -> str:
    """
    创建刷新令牌

    Args:
        subject: 令牌主题
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        JWT刷新令牌
    """
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码令牌

    Args:
        token: JWT令牌

    Returns:
        解码后的载荷，无效返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    验证令牌

    Args:
        token: JWT令牌
        token_type: 令牌类型 (access/refresh)

    Returns:
        验证成功返回载荷，失败返回None
    """
    payload = decode_token(token)
    if payload is None:
        return None

    # 检查令牌类型
    if payload.get("type") != token_type:
        return None

    # 检查过期时间
    exp = payload.get("exp")
    if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
        return None

    return payload