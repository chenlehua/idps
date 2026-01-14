# 车辆入侵检测系统 (IDPS)

## 项目概述

IDPS (Intrusion Detection and Prevention System) 是一套完整的车辆入侵检测系统，包括车端检测组件和云端管理平台，提供网络、防火墙和主机层面的入侵检测与防护能力。

### 主要特性

- **多层防护**: 网络层（基于Suricata）、防火墙层（基于eBPF/XDP）、主机层（基于Audit）
- **云端管理**: 集中式规则管理、日志收集分析、车辆状态监控
- **双向认证**: HTTPS双向TLS认证，确保车云通信安全
- **GPL隔离**: 通过进程隔离避免GPL许可证传染
- **高性能**: eBPF/XDP零拷贝技术，低CPU占用
- **可扩展**: 微服务架构，支持水平扩展

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      云端平台                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 认证服务 │ │ 规则服务 │ │ 日志服务 │ │ 车辆管理 │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌────────────┐ ┌────────┐               │
│  │  MySQL   │ │ ClickHouse │ │ Redis  │               │
│  └──────────┘ └────────────┘ └────────┘               │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTPS双向认证
┌─────────────────────────────────────────────────────────┐
│                      车端系统                            │
│  ┌─────────────────────────────────────────┐            │
│  │         车云交互组件 (Connector)         │            │
│  └─────────────────────────────────────────┘            │
│         ↓              ↓              ↓                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 网络探针 │  │ 防火墙   │  │ 主机探针 │              │
│  │(Suricata)│  │(eBPF/XDP)│  │(Audit)   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 项目结构

```
idps/
├── vehicle/              # 车端组件 (C语言)
│   ├── src/
│   │   ├── common/      # 公共库
│   │   ├── connector/   # 车云交互组件
│   │   ├── network_probe/   # 网络入侵检测探针
│   │   ├── firewall_probe/  # 防火墙探针 (eBPF)
│   │   ├── host_probe/      # 主机入侵检测探针
│   │   └── daemon/          # 主守护进程
│   ├── include/         # 头文件
│   ├── tests/           # 单元测试
│   └── CMakeLists.txt   # 构建配置
│
├── cloud/                # 云端后端 (Python)
│   ├── common/          # 公共库
│   ├── auth_service/    # 认证服务
│   ├── rule_service/    # 规则服务
│   ├── log_service/     # 日志服务
│   ├── vehicle_service/ # 车辆管理服务
│   └── requirements.txt # Python依赖
│
├── frontend/            # 前端界面 (React + TypeScript)
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docker/              # Docker配置
│   ├── mysql/          # MySQL配置和初始化脚本
│   ├── clickhouse/     # ClickHouse配置和初始化脚本
│   ├── redis/          # Redis配置
│   └── nginx/          # Nginx反向代理配置
│
├── scripts/             # 工具脚本
│   └── init_db.py      # 数据库初始化脚本
│
├── specs/               # 设计文档
│   ├── 0001-prd.md                   # 产品需求文档
│   ├── 0002-design.md                # 详细设计文档
│   └── 0003-implementation-plan.md   # 实施计划
│
├── docker compose.yml   # Docker Compose配置
├── .gitlab-ci.yml       # GitLab CI/CD配置
└── README.md            # 本文件
```

## 技术栈

### 车端 (Vehicle)
- **语言**: C (C11)
- **构建**: CMake 3.15+
- **依赖**:
  - OpenSSL 1.1.1+ (TLS/加密)
  - libjansson (JSON)
  - libbpf (eBPF)
  - Suricata 7.0+ (IDS引擎)
- **系统**: Linux 5.10+, ARM64

### 云端后端 (Cloud)
- **语言**: Python 3.11+
- **框架**: Flask 3.0
- **包管理**: uv (极速 Python 包管理器)
- **数据库**:
  - MySQL 8.0 (关系数据)
  - ClickHouse 23.8 (日志存储)
  - Redis 7.0 (缓存)
- **ORM**: SQLAlchemy 2.0
- **部署**: Docker + Docker Compose

### 前端 (Frontend)
- **语言**: TypeScript 5.0+
- **框架**: React 18+
- **UI库**: Ant Design 5.0+
- **图表**: ECharts 5.0+
- **构建**: Vite

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Make (构建工具)
- Python 3.11+ (用于运行脚本)
- uv (Python 包管理器) - [安装指南](docs/UV_GUIDE.md#安装-uv)

**重要**: 确保当前用户在 docker 组中，否则需要使用 sudo:
```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER
# 需要重新登录生效
```

### 构建系统

项目使用 Make 作为统一的构建工具。查看可用命令:

```bash
# 查看所有可用命令
make help

# 查看特定模块的命令
cd vehicle && make help
cd cloud && make help
cd frontend && make help
```

详细的 Makefile 使用说明请参考 [Makefile 使用指南](docs/MAKEFILE.md)。

### 1. 克隆项目

```bash
git clone https://github.com/your-org/idps.git
cd idps
```

### 2. 检查构建工具

```bash
# 检查系统依赖
bash scripts/check-deps.sh

# 或使用 make
make check-tools
```

### 3. 启动开发环境

```bash
# 启动数据库服务
make dev-up

# 等待服务启动
sleep 10
```

### 4. 初始化数据库

```bash
# 会自动安装依赖（如果需要）
make db-init
```

### 5. 构建项目

```bash
# 构建所有模块
make build

# 或分别构建
make vehicle-build    # 构建车端
make cloud-build      # 安装云端依赖
make frontend-build   # 构建前端
```

### 6. 运行测试

```bash
# 运行所有测试
make test

# 或分别测试
make vehicle-test
make cloud-test
make frontend-test
```

### 7. 启动云端服务

```bash
# 方式1: 使用 Docker Compose（推荐）
docker compose up -d

# 方式2: 本地开发模式
cd cloud && make dev-auth &
cd cloud && make dev-rule &
cd cloud && make dev-log &
cd cloud && make dev-vehicle &
```

### 8. 启动前端

```bash
cd frontend
make dev
```

访问 http://localhost:3000

默认管理员账号:
- 用户名: `admin`
- 密码: `Admin@123456`

### 9. 构建车端组件

```bash
cd vehicle

# 本地构建（ARM64平台）
make build

# 交叉编译（x86_64平台）
make build-cross

# 运行测试
make test
```

## 开发指南

### 车端开发

参见 [vehicle/README.md](vehicle/README.md)

- 代码规范: Linux内核编码规范
- 构建系统: CMake
- 单元测试: CUnit/Check
- 目标平台: Linux 5.10+ ARM64

### 云端后端开发

参见 [cloud/README.md](cloud/README.md) 和 [uv 使用指南](docs/UV_GUIDE.md)

- 代码规范: PEP 8
- 包管理: uv (极速包管理器)
- 格式化: black
- 代码检查: ruff + flake8
- 类型检查: mypy
- 单元测试: pytest

快速开始:
```bash
cd cloud

# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
make install-dev

# 运行测试
make test

# 代码检查
make lint
```

### 前端开发

参见 [frontend/README.md](frontend/README.md)

- 代码规范: Airbnb
- 格式化: Prettier
- 代码检查: ESLint
- 类型检查: TypeScript
- 单元测试: Jest + React Testing Library

## 部署

### 开发环境

```bash
docker compose up -d
```

### 生产环境

```bash
# 1. 修改环境变量
cp cloud/.env.example cloud/.env
vim cloud/.env  # 配置生产环境参数

# 2. 部署
docker compose -f docker compose.prod.yml up -d
```

详细部署说明请参考文档。

## 测试

```bash
# 运行所有测试
make test

# 车端测试
cd vehicle && make test

# 云端测试
cd cloud && make test

# 前端测试
cd frontend && make test

# 查看测试覆盖率
cd cloud && make test-coverage    # 云端覆盖率
cd frontend && make test-coverage # 前端覆盖率
```

## CI/CD

项目使用 GitHub Actions 进行持续集成和部署。工作流配置文件位于 `.github/workflows/` 目录。

### 工作流说明

#### 1. Vehicle CI (`.github/workflows/vehicle-ci.yml`)
车端组件的持续集成流水线：
- **lint**: 代码格式检查 (clang-format)
- **test**: 单元测试
- **build**: ARM64 交叉编译构建

#### 2. Cloud Backend CI (`.github/workflows/cloud-ci.yml`)
云端后端服务的持续集成流水线：
- **lint**: 代码检查 (black, flake8, mypy)
- **test**: 单元测试和覆盖率
- **build-***: 构建并推送 Docker 镜像到 GitHub Container Registry
  - auth-service (认证服务)
  - rule-service (规则服务)
  - log-service (日志服务)
  - vehicle-service (车辆管理服务)

#### 3. Frontend CI (`.github/workflows/frontend-ci.yml`)
前端应用的持续集成流水线：
- **lint**: ESLint 代码检查和 TypeScript 类型检查
- **test**: 单元测试和覆盖率
- **build**: 构建生产版本
- **build-docker**: 构建并推送 Docker 镜像

#### 4. Deploy (`.github/workflows/deploy.yml`)
部署工作流：
- **deploy-staging**: 部署到测试环境 (develop 分支自动触发)
- **deploy-production**: 部署到生产环境 (main 分支自动触发)
- 支持手动触发部署 (workflow_dispatch)

### 触发条件

- **Push**: 当代码推送到 `main` 或 `develop` 分支时触发
- **Pull Request**: 当创建或更新 PR 时触发
- **Path Filters**: 只在相关文件变更时触发对应的工作流

### 必需的 Secrets

在 GitHub 仓库设置中配置以下 Secrets：

- `SSH_PRIVATE_KEY`: SSH 私钥，用于连接部署服务器
- `STAGING_HOST`: 测试环境服务器地址
- `STAGING_USER`: 测试环境 SSH 用户名
- `PRODUCTION_HOST`: 生产环境服务器地址
- `PRODUCTION_USER`: 生产环境 SSH 用户名

注意：`GITHUB_TOKEN` 会自动提供，用于推送 Docker 镜像到 GitHub Container Registry。

## 文档

- [产品需求文档 (PRD)](specs/0001-prd.md)
- [详细设计文档](specs/0002-design.md)
- [实施计划](specs/0003-implementation-plan.md)
- [Makefile 使用指南](docs/MAKEFILE.md)
- [uv Python 包管理指南](docs/UV_GUIDE.md)
- [GitHub Actions 配置指南](docs/GITHUB_ACTIONS.md)
- [API文档](http://localhost:5001/api/docs) (启动服务后访问)

## 许可证

本项目采用私有许可证。与GPL组件（Suricata）通过进程隔离避免许可证传染。

## 贡献

请参考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献代码。

## 联系方式

- 项目主页: https://gitlab.com/idps/idps
- 问题反馈: https://gitlab.com/idps/idps/issues
- 技术支持: support@idps.example.com
- 文档中心: https://docs.idps.example.com

## 致谢

本项目使用了以下开源项目:
- [Suricata](https://suricata.io/) - 网络入侵检测引擎
- [eBPF/libbpf](https://ebpf.io/) - 内核可编程框架
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [React](https://react.dev/) - 前端UI框架
- [ClickHouse](https://clickhouse.com/) - OLAP数据库
