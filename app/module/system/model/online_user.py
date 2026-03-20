"""
在线用户模型（基于Redis存储）
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class OnlineUser:
    """在线用户信息"""

    user_id: int
    username: str
    nickname: str
    dept_id: Optional[int] = None
    dept_name: Optional[str] = None
    token: str = ""
    session_timeout: Optional[datetime] = None

    # 客户端信息
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    login_time: Optional[datetime] = None

    # 租户
    tenant_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "userId": self.user_id,
            "username": self.username,
            "nickname": self.nickname,
            "deptId": self.dept_id,
            "deptName": self.dept_name,
            "userIp": self.user_ip,
            "browser": self.browser,
            "os": self.os,
            "loginTime": self.login_time.isoformat() if self.login_time else None,
            "tenantId": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OnlineUser":
        return cls(
            user_id=data.get("userId", 0),
            username=data.get("username", ""),
            nickname=data.get("nickname", ""),
            dept_id=data.get("deptId"),
            dept_name=data.get("deptName"),
            user_ip=data.get("userIp"),
            browser=data.get("browser"),
            os=data.get("os"),
            login_time=datetime.fromisoformat(data["loginTime"]) if data.get("loginTime") else None,
            tenant_id=data.get("tenantId"),
        )