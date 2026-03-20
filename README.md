# Yudao FastAPI

基于 FastAPI 的企业级后台管理系统，迁移自 ruoyi-vue-pro (Java)。

## 技术栈

| Java技术 | FastAPI技术 | 版本 |
|---------|------------|------|
| Spring Boot 2.7 | FastAPI | 0.115+ |
| Spring Security | python-jose + passlib | 3.3.0 / 1.7.4 |
| MyBatis-Plus | SQLAlchemy | 2.0.36+ |
| Druid | aiomysql | 0.2.0 |
| Redisson | redis-py | 5.2.0 |
| Knife4j | 内置Swagger UI | - |
| Lombok | Pydantic | 2.10+ |
| Spring Task | APScheduler | 3.10+ |
| Lock4j | 自定义Redis锁 | - |

## 项目结构

```
yudao-fastapi/
├── app/
│   ├── core/                    # 核心组件
│   │   ├── database.py          # 数据库连接
│   │   ├── redis.py             # Redis连接
│   │   ├── security.py          # JWT认证
│   │   ├── tenant.py            # 多租户支持
│   │   ├── lock.py              # 分布式锁
│   │   ├── scheduler.py         # 定时任务
│   │   ├── metrics.py           # Prometheus监控
│   │   ├── exceptions.py        # 异常定义
│   │   └── dependencies.py      # FastAPI依赖
│   ├── middleware/              # 中间件
│   │   ├── tenant.py            # 租户中间件
│   │   ├── logging.py           # 日志中间件
│   │   └── auth.py              # 认证中间件
│   ├── module/system/           # 系统模块
│   │   ├── controller/          # API控制器
│   │   ├── service/             # 业务服务
│   │   ├── model/               # 数据库模型
│   │   ├── schema/              # Pydantic模型
│   │   └── repository/          # 数据访问
│   ├── common/                  # 公共组件
│   │   ├── response.py          # 统一响应
│   │   ├── pagination.py        # 分页处理
│   │   └── utils.py             # 工具函数
│   └── extensions/              # 扩展功能
│       ├── captcha.py           # 验证码
│       └── storage.py           # 文件存储
├── migrations/                  # Alembic迁移
├── tests/                       # 测试用例
├── scripts/                     # 脚本文件
│   ├── init_db.py               # 数据库初始化
│   └── scheduled_tasks.py       # 定时任务示例
├── requirements.txt             # 依赖文件
├── pyproject.toml               # 项目配置
├── Dockerfile                   # Docker配置
├── docker-compose.yml           # 容器编排
└── README.md                    # 项目文档
```

## 功能模块

### ✅ 第一阶段：基础架构
- [x] 项目骨架搭建
- [x] 数据库连接（SQLAlchemy异步）
- [x] Redis连接与缓存
- [x] JWT认证授权
- [x] 多租户支持（contextvars）
- [x] 统一响应格式
- [x] 全局异常处理
- [x] API文档（Swagger UI）
- [x] 分布式锁（Redis）
- [x] 定时任务（APScheduler）
- [x] Prometheus监控指标

### ✅ 第二阶段：系统模块
| 模块 | 功能 | 状态 |
|-----|------|------|
| 用户管理 | CRUD、密码修改、重置密码 | ✅ |
| 角色管理 | 基础查询、角色分配 | ✅ |
| 菜单管理 | 菜单树、权限标识 | ✅ |
| 部门管理 | 部门树、层级查询 | ✅ |
| 岗位管理 | 基础查询 | ✅ |
| 字典管理 | 类型管理、数据管理、缓存 | ✅ |

### ✅ 第三阶段：扩展功能
| 功能 | 状态 | 说明 |
|-----|------|------|
| 操作日志 | ✅ | 记录API操作、装饰器支持 |
| 登录日志 | ✅ | 登录/登出记录、UA解析 |
| 在线用户 | ✅ | Redis存储、踢出用户 |
| 参数配置 | ✅ | 系统参数、缓存支持 |
| 数据权限 | ✅ | 部门层级权限过滤 |
| 文件存储 | ✅ | 本地存储、S3支持 |
| 验证码 | ✅ | 图片验证码生成 |

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd yudao-fastapi

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
vim .env
```

### 3. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE \`ruoyi-vue-pro\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 初始化表结构和数据
python scripts/init_db.py
```

### 4. 启动

```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Docker 部署

```bash
docker-compose up -d
```

## API 文档

启动后访问:
- Swagger UI: http://localhost:8000/admin-api/docs
- ReDoc: http://localhost:8000/admin-api/redoc
- Prometheus: http://localhost:8000/metrics

## 核心功能示例

### 多租户使用

```python
from app.core.tenant import get_tenant_id, set_tenant

# 设置租户
set_tenant(1)

# 获取当前租户
tenant_id = get_tenant_id()
```

### 权限控制

```python
from app.core.dependencies import check_permission

@router.get("/users", dependencies=[Depends(check_permission("system:user:list"))])
async def list_users():
    ...
```

### 分布式锁

```python
from app.core.lock import distributed_lock

async with distributed_lock("user:1:update", timeout=30):
    # 执行需要加锁的操作
    ...
```

### 定时任务

```python
from app.core.scheduler import scheduled

@scheduled(cron="0 9 * * *")
async def daily_report():
    # 每天9点执行
    ...
```

### 数据权限

```python
from app.module.system.service import get_data_permission_filter

# 获取带权限过滤的查询
query = await get_data_permission_filter(db, user_id, User)
result = await db.execute(query.where(User.status == 0))
```

## 开发指南

### 创建新模块

```python
# app/module/new_module/
├── controller/    # API控制器
├── service/       # 业务服务
├── repository/    # 数据访问
├── model/         # 数据库模型
└── schema/        # Pydantic模型
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

### 运行测试

```bash
pytest
```

## 默认账号

- 用户名: `admin`
- 密码: `admin123`

## License

MIT