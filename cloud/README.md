# IDPS Cloud - 云端管理平台

## 概述

IDPS Cloud 是车辆入侵检测系统的云端管理平台，提供车辆管理、规则配置、日志查询等功能。

## 技术栈

- **后端框架**: Flask 3.0
- **数据库**: MySQL 8.0, ClickHouse 23.8, Redis 7.0
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT
- **部署**: Docker + Docker Compose

## 项目结构

```
cloud/
├── common/                 # 公共库
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── middleware/        # 中间件（认证、日志、错误处理）
│   ├── utils/             # 工具函数
│   └── models/            # 数据模型
├── auth_service/          # 认证服务
├── rule_service/          # 规则服务
├── log_service/           # 日志服务
├── vehicle_service/       # 车辆管理服务
├── tests/                 # 测试
├── requirements.txt       # Python依赖
└── .env.example          # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置数据库连接等信息
vim .env
```

### 3. 初始化数据库

```bash
# 进入项目根目录
cd ..

# 启动数据库服务（使用Docker Compose）
docker compose up -d mysql redis clickhouse

# 初始化数据库表结构
python scripts/init_db.py
```

### 4. 运行开发服务器

```bash
# 认证服务
cd auth_service
python app.py

# 规则服务
cd rule_service
python app.py

# 日志服务
cd log_service
python app.py

# 车辆管理服务
cd vehicle_service
python app.py
```

### 5. 使用Docker Compose运行

```bash
# 在项目根目录
docker compose up -d
```

所有服务将在以下端口启动：
- 认证服务: http://localhost:5001
- 规则服务: http://localhost:5002
- 日志服务: http://localhost:5003
- 车辆管理服务: http://localhost:5004

## 服务说明

### 1. 认证服务 (auth_service)

负责车辆认证和Token管理：

- `POST /api/v1/vehicle/register` - 车辆注册
- `POST /api/v1/auth/refresh` - Token刷新
- `POST /api/v1/vehicle/heartbeat` - 心跳

### 2. 规则服务 (rule_service)

负责规则管理和下发：

- `POST /api/v1/rule/query` - 查询规则版本
- `GET /api/v1/rule/download` - 下载规则
- `POST /api/v1/rule/version` - 创建规则版本
- `POST /api/v1/rule/publish` - 发布规则

### 3. 日志服务 (log_service)

负责日志收集和查询：

- `POST /api/v1/log/upload` - 上报日志
- `POST /api/v1/log/batch` - 批量上报
- `GET /api/v1/log/query` - 查询日志
- `GET /api/v1/log/stats` - 日志统计

### 4. 车辆管理服务 (vehicle_service)

负责车辆信息管理：

- `GET /api/v1/vehicle/list` - 车辆列表
- `GET /api/v1/vehicle/:vin` - 车辆详情
- `PUT /api/v1/vehicle/:vin` - 更新车辆
- `DELETE /api/v1/vehicle/:vin` - 删除车辆

## 开发指南

### 代码规范

- 遵循PEP 8规范
- 使用black格式化代码
- 使用flake8检查代码
- 使用mypy进行类型检查

```bash
# 格式化代码
black .

# 代码检查
flake8 .

# 类型检查
mypy .
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 数据库迁移

使用Alembic进行数据库版本管理：

```bash
# 创建迁移脚本
alembic revision --autogenerate -m "描述"

# 升级到最新版本
alembic upgrade head

# 回退一个版本
alembic downgrade -1
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:5001/api/docs

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t idps-auth-service:latest -f auth_service/Dockerfile .
docker build -t idps-rule-service:latest -f rule_service/Dockerfile .
docker build -t idps-log-service:latest -f log_service/Dockerfile .
docker build -t idps-vehicle-service:latest -f vehicle_service/Dockerfile .

# 使用Docker Compose部署
docker compose -f docker compose.prod.yml up -d
```

### 生产环境配置

1. 修改`.env`文件，配置生产环境参数
2. 设置强密码和密钥
3. 配置SSL证书
4. 配置反向代理（Nginx）
5. 配置监控和日志收集

## 监控

- **健康检查**: `GET /health`
- **指标**: `GET /metrics` (Prometheus格式)

## 故障排查

### 数据库连接失败

```bash
# 检查数据库服务状态
docker compose ps

# 查看数据库日志
docker compose logs mysql
```

### 服务启动失败

```bash
# 查看服务日志
docker compose logs auth_service

# 进入容器调试
docker compose exec auth_service bash
```

## 安全注意事项

1. **密钥管理**: 生产环境必须修改SECRET_KEY和JWT_SECRET_KEY
2. **数据库密码**: 使用强密码，不要使用默认密码
3. **SSL/TLS**: 启用HTTPS和双向认证
4. **限流**: 配置合理的API限流策略
5. **日志**: 不要在日志中记录敏感信息

## 许可证

本项目采用私有许可证。

## 联系方式

- 问题反馈: [Issues](https://gitlab.com/idps/cloud/issues)
- 技术支持: support@idps.example.com
