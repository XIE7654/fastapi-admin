"""
工具函数
"""
import uuid
from datetime import datetime
from typing import Optional
import time


class SnowflakeIdGenerator:
    """雪花ID生成器"""

    def __init__(self, worker_id: int = 1, datacenter_id: int = 1):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1

        # 起始时间戳 (2024-01-01)
        self.twepoch = 1704038400000

        # 位数
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        # 最大值
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        # 位移
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = (
            self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        )

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp

    def generate(self) -> int:
        """生成下一个ID"""
        timestamp = self._current_millis()

        if timestamp < self.last_timestamp:
            raise RuntimeError("时钟回拨，无法生成ID")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return (
            ((timestamp - self.twepoch) << self.timestamp_left_shift)
            | (self.datacenter_id << self.datacenter_id_shift)
            | (self.worker_id << self.worker_id_shift)
            | self.sequence
        )


# 全局雪花ID生成器
_snowflake = SnowflakeIdGenerator()


def get_current_datetime() -> datetime:
    """获取当前时间"""
    return datetime.now()


def datetime_to_str(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    datetime转字符串

    Args:
        dt: datetime对象
        fmt: 格式字符串

    Returns:
        格式化后的字符串，None返回None
    """
    if dt is None:
        return None
    return dt.strftime(fmt)


def str_to_datetime(
    date_str: Optional[str],
    fmt: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    字符串转datetime

    Args:
        date_str: 时间字符串
        fmt: 格式字符串

    Returns:
        datetime对象，空字符串返回None
    """
    if not date_str:
        return None
    return datetime.strptime(date_str, fmt)


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4()).replace("-", "")


def generate_snowflake_id() -> int:
    """生成雪花ID"""
    return _snowflake.generate()


def mask_phone(phone: str) -> str:
    """
    手机号脱敏

    Args:
        phone: 手机号

    Returns:
        脱敏后的手机号
    """
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def mask_email(email: str) -> str:
    """
    邮箱脱敏

    Args:
        email: 邮箱地址

    Returns:
        脱敏后的邮箱
    """
    if not email or "@" not in email:
        return email
    parts = email.split("@")
    name = parts[0]
    if len(name) <= 2:
        return name[0] + "***@" + parts[1]
    return name[:2] + "***" + name[-1] + "@" + parts[1]


def parse_optional_int(value: Optional[str]) -> Optional[int]:
    """
    解析可选的整数参数，将空字符串转换为 None

    Args:
        value: 字符串值，可能为空字符串或 None

    Returns:
        整数或 None
    """
    if value is None or value == "":
        return None
    return int(value)