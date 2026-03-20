"""
核心组件模块
"""
from app.core.database import get_db, init_db, close_db
from app.core.redis import get_redis, init_redis, close_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from app.core.tenant import get_tenant, set_tenant, get_tenant_id
from app.core.dependencies import get_current_user, check_permission
from app.core.lock import DistributedLock, distributed_lock, try_lock, Lock4j
from app.core.scheduler import (
    init_scheduler,
    start_scheduler,
    shutdown_scheduler,
    add_cron_job,
    add_interval_job,
    scheduled,
)
from app.core.metrics import (
    track_request,
    track_request_latency,
    track_user_login,
    track_api_call,
    track_cache_hit,
    track_cache_miss,
    set_online_users,
    metrics_endpoint,
)

__all__ = [
    # Database
    "get_db",
    "init_db",
    "close_db",
    # Redis
    "get_redis",
    "init_redis",
    "close_redis",
    # Security
    "create_access_token",
    "create_refresh_token",
    "verify_password",
    "get_password_hash",
    "decode_token",
    # Tenant
    "get_tenant",
    "set_tenant",
    "get_tenant_id",
    # Dependencies
    "get_current_user",
    "check_permission",
    # Lock
    "DistributedLock",
    "distributed_lock",
    "try_lock",
    "Lock4j",
    # Scheduler
    "init_scheduler",
    "start_scheduler",
    "shutdown_scheduler",
    "add_cron_job",
    "add_interval_job",
    "scheduled",
    # Metrics
    "track_request",
    "track_request_latency",
    "track_user_login",
    "track_api_call",
    "track_cache_hit",
    "track_cache_miss",
    "set_online_users",
    "metrics_endpoint",
]