# IDPS 开发指南

本文档详细说明 IDPS 项目的开发环境搭建、开发流程和最佳实践。

## 目录

- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [快速开始](#快速开始)
- [构建系统](#构建系统)
- [车端开发](#车端开发)
- [云端开发](#云端开发)
- [前端开发](#前端开发)
- [测试指南](#测试指南)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)
- [开发工作流](#开发工作流)
- [CI/CD](#cicd)
- [开发工具](#开发工具)
- [故障排除](#故障排除)
- [参考资源](#参考资源)

## 系统要求

### 基础要求

- **操作系统**: Linux (Ubuntu 20.04+推荐) 或 macOS
- **内存**: 最少 8GB，推荐 16GB+
- **硬盘**: 至少 50GB 可用空间
- **网络**: 稳定的互联网连接（用于下载依赖）

### 软件要求

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| Docker | 20.10+ | 容器化部署 |
| Docker Compose | 2.0+ | 多容器编排 |
| Make | 4.0+ | 构建工具 |
| Python | 3.11+ | 云端开发 |
| uv | 0.4+ | Python 包管理 |
| Node.js | 20+ | 前端开发 |
| GCC | 11+ | 车端编译 |
| CMake | 3.15+ | 车端构建 |
| Git | 2.30+ | 版本控制 |

## 环境准备

### 1. 安装 Docker 和 Docker Compose

#### Ubuntu/Debian

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加当前用户到docker组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

#### macOS

```bash
# 下载并安装 Docker Desktop for Mac
# https://www.docker.com/products/docker-desktop

# 或使用 Homebrew
brew install --cask docker
```

### 2. 安装 Make

```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install

# 验证安装
make --version
```

### 3. 安装 Python 和 uv

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# 安装 uv (极速 Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS
brew install python@3.11
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
python3 --version
uv --version
```

### 4. 安装 Node.js

```bash
# 使用nvm安装（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# 验证安装
node --version
npm --version
```

### 5. 安装车端开发工具

```bash
# Ubuntu/Debian
sudo apt-get install \
    build-essential \
    cmake \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    libssl-dev \
    libjansson-dev \
    libbpf-dev \
    pkg-config \
    clang-format \
    linux-headers-$(uname -r)

# 验证安装
gcc --version
cmake --version
aarch64-linux-gnu-gcc --version
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/idps.git
cd idps
```

### 2. 检查构建工具

```bash
# 检查所有必需工具是否已安装
make check-tools
```

### 3. 启动开发环境

```bash
# 启动数据库服务
make dev-up

# 等待服务启动
sleep 10

# 初始化数据库
make db-init
```

### 4. 验证环境

```bash
# 查看服务状态
make dev-ps

# 查看服务日志
make dev-logs
```

## 构建系统

项目使用 Make 作为统一的构建工具。详细文档请参考 [Makefile 使用指南](./MAKEFILE.md)。

### 常用命令

```bash
# 查看所有可用命令
make help

# 构建所有模块
make build

# 运行所有测试
make test

# 运行代码检查
make lint

# 清理构建产物
make clean

# 显示项目信息
make info
make version
```

### 模块命令

```bash
# 车端
make vehicle-build        # 构建车端
make vehicle-build-cross  # 交叉编译 (ARM64)
make vehicle-test         # 运行测试
make vehicle-lint         # 代码检查

# 云端
make cloud-build          # 安装依赖
make cloud-test           # 运行测试
make cloud-lint           # 代码检查
make cloud-docker         # 构建 Docker 镜像

# 前端
make frontend-build       # 构建前端
make frontend-test        # 运行测试
make frontend-lint        # 代码检查
make frontend-docker      # 构建 Docker 镜像
```

## 车端开发

车端使用 C 语言开发，详细文档参考 [vehicle/README.md](../vehicle/README.md)。

### 开发环境设置

```bash
cd vehicle

# 检查依赖
make deps

# 本地构建（需要 ARM64 平台）
make build

# 交叉编译（x86_64 平台）
make build-cross

# Debug 构建
make build-debug
```

### 运行测试

```bash
# 运行所有测试
make test

# 详细输出
make test-verbose
```

### 代码质量

```bash
# 检查代码格式
make lint

# 自动格式化代码
make format

# 静态分析
make static-analysis
```

### 开发调试

#### 使用 GDB 调试

```bash
# 构建 Debug 版本
make build-debug

# 启动 GDB
cd build-debug
gdb ./src/daemon/idps_daemon

# GDB 命令
(gdb) break main
(gdb) run
(gdb) next
(gdb) print variable_name
(gdb) backtrace
```

#### 使用 AddressSanitizer

```bash
# 构建启用 ASAN 的版本
mkdir build-asan && cd build-asan
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON
make

# 运行程序
./src/daemon/idps_daemon
```

### 性能分析

```bash
# 使用 valgrind 检查内存泄漏
valgrind --leak-check=full --show-leak-kinds=all ./idps_daemon

# 使用 perf 进行性能分析
perf record -g ./idps_daemon
perf report
```

## 云端开发

云端使用 Python 3.11+ 和 uv 包管理器。详细文档参考：
- [cloud/README.md](../cloud/README.md)
- [uv 使用指南](./UV_GUIDE.md)

### 开发环境设置

```bash
cd cloud

# 检查 uv 是否已安装
make check-uv

# 如果未安装，运行:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装开发依赖
make install-dev

# 或使用 uv 直接安装
uv sync --all-extras
```

### 项目结构

```
cloud/
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 依赖锁文件
├── Makefile              # 构建配置
├── common/               # 公共库
├── auth_service/         # 认证服务
├── rule_service/         # 规则服务
├── log_service/          # 日志服务
└── vehicle_service/      # 车辆管理服务
```

### 启动开发服务器

```bash
# 启动单个服务（使用 uv run）
make dev-auth           # 认证服务 (端口 5001)
make dev-rule           # 规则服务 (端口 5002)
make dev-log            # 日志服务 (端口 5003)
make dev-vehicle        # 车辆管理 (端口 5004)

# 或直接使用 uv
cd auth_service
uv run python app.py
```

### 依赖管理

```bash
# 添加生产依赖
make add PKG=requests

# 添加开发依赖
make add-dev PKG=pytest-mock

# 移除依赖
make remove PKG=requests

# 升级所有依赖
make upgrade

# 查看依赖树
make tree

# 锁定依赖版本
make lock
```

### 代码质量

```bash
# 运行所有检查
make lint

# 单独运行
make format-check       # 检查代码格式
make format             # 自动格式化
make ruff               # 运行 ruff 检查
make ruff-fix           # 自动修复 ruff 问题
make flake8             # 运行 flake8
make mypy               # 类型检查
```

### 测试

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 生成覆盖率报告
make test-coverage
# 报告位置: htmlcov/index.html
```

### 数据库操作

```bash
# 连接 MySQL
docker compose exec mysql mysql -u idps -pidps123456 idps

# 连接 ClickHouse
docker compose exec clickhouse clickhouse-client --database idps

# 连接 Redis
docker compose exec redis redis-cli
```

## 前端开发

前端使用 React + TypeScript + Vite。详细文档参考 [frontend/README.md](../frontend/README.md)。

### 开发环境设置

```bash
cd frontend

# 安装依赖
make install

# 或使用 npm
npm ci
```

### 启动开发服务器

```bash
# 启动开发服务器
make dev

# 允许外部访问
make dev-host

# 访问: http://localhost:3000
```

### 代码质量

```bash
# 运行所有检查
make lint

# ESLint 检查
make lint

# 自动修复
make lint-fix

# TypeScript 类型检查
make type-check

# 代码格式化
make format

# 检查格式
make format-check
```

### 测试

```bash
# 运行测试
make test

# 监听模式
make test-watch

# 生成覆盖率
make test-coverage
```

### 构建

```bash
# 构建生产版本
make build

# 预览生产构建
make preview

# 分析构建产物
make analyze
```

## 测试指南

### 单元测试

#### 车端 (C)

```bash
cd vehicle
make test

# 测试在 tests/ 目录
# 使用 CUnit 或 Check 框架
```

#### 云端 (Python)

```bash
cd cloud
make test

# 测试在各服务的 tests/ 目录
# 使用 pytest 框架
```

示例测试:

```python
# tests/test_auth.py
import pytest
from auth_service.app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_login(client):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin@123456'
    })
    assert response.status_code == 200
    assert 'token' in response.json
```

#### 前端 (TypeScript)

```bash
cd frontend
make test

# 测试在 src/ 目录，文件名 *.test.tsx
# 使用 Jest + React Testing Library
```

示例测试:

```typescript
// src/components/Login.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Login from './Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByLabelText('Username')).toBeInTheDocument();
  expect(screen.getByLabelText('Password')).toBeInTheDocument();
});
```

### 集成测试

```bash
# 云端集成测试
cd cloud
make test-integration

# 需要数据库服务运行
make dev-up
```

### 端到端测试

```bash
# 使用 Playwright（如果配置）
cd frontend
npm run test:e2e
```

## 代码规范

### 车端 (C)

- 遵循 Linux 内核编码规范
- 使用 clang-format 自动格式化
- 函数名使用小写下划线分隔
- 结构体使用 `_t` 后缀

```c
// 示例
typedef struct {
    int id;
    char name[64];
} vehicle_t;

int vehicle_create(vehicle_t *vehicle);
void vehicle_destroy(vehicle_t *vehicle);
```

### 云端 (Python)

- 遵循 PEP 8 规范
- 使用 black 格式化（行长 100）
- 使用 ruff 进行代码检查
- 使用类型注解

```python
# 示例
from typing import Optional

def get_user_by_id(user_id: int) -> Optional[dict]:
    """获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        用户信息字典，如果不存在返回 None
    """
    # 实现
    pass
```

### 前端 (TypeScript)

- 遵循 Airbnb 规范
- 使用 Prettier 格式化
- 使用 ESLint 检查
- 组件使用 PascalCase

```typescript
// 示例
interface LoginProps {
  onSuccess: () => void;
  onError: (error: Error) => void;
}

export const Login: React.FC<LoginProps> = ({ onSuccess, onError }) => {
  // 实现
};
```

## 调试技巧

### 车端调试

#### 打印调试

```c
#include <stdio.h>

#define DEBUG_PRINT(fmt, ...) \
    fprintf(stderr, "[DEBUG] %s:%d: " fmt "\n", \
            __FILE__, __LINE__, ##__VA_ARGS__)

// 使用
DEBUG_PRINT("Vehicle ID: %d", vehicle->id);
```

#### GDB 技巧

```bash
# 条件断点
(gdb) break main if vehicle_id == 123

# 监视点
(gdb) watch variable_name

# 打印结构体
(gdb) print *vehicle

# 调用栈
(gdb) backtrace full
```

### 云端调试

#### 使用 pdb

```python
import pdb

def process_data(data):
    pdb.set_trace()  # 设置断点
    # 代码
```

#### 使用 VSCode 调试

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_DEBUG": "1"
      },
      "args": ["run", "--no-debugger"],
      "jinja": true
    }
  ]
}
```

#### 日志调试

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Variable value: %s", value)
logger.info("Processing started")
logger.warning("Deprecated feature used")
logger.error("Error occurred: %s", error)
```

### 前端调试

#### 浏览器开发工具

- Chrome DevTools (F12)
- React Developer Tools
- Redux DevTools

#### console 调试

```typescript
console.log('Value:', value);
console.table(arrayOfObjects);
console.time('operation');
// ... code
console.timeEnd('operation');
```

#### VSCode 调试

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

## 开发工作流

### 分支策略

```
main (生产环境，受保护)
  │
  └─ develop (开发环境)
       │
       ├─ feature/user-auth      (功能分支)
       ├─ feature/log-service    (功能分支)
       ├─ bugfix/memory-leak     (修复分支)
       └─ hotfix/security-patch  (紧急修复)
```

### 开发流程

1. **创建分支**

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 从 main 创建紧急修复分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix
```

2. **开发和测试**

```bash
# 编写代码
vim src/my_feature.c

# 运行测试
make test

# 代码检查
make lint

# 提交更改
git add .
git commit -m "feat(module): add new feature"
```

3. **推送和创建 PR**

```bash
# 推送分支
git push origin feature/my-feature

# 在 GitHub 上创建 Pull Request
# 或使用命令行
gh pr create --title "Add new feature" --body "Description"
```

4. **代码审查**

- 至少 1 人审核
- CI 检查必须通过
- 解决所有评论

5. **合并**

```bash
# 合并到 develop（功能分支）
# 或合并到 main（hotfix）

# 删除本地分支
git branch -d feature/my-feature

# 删除远程分支
git push origin --delete feature/my-feature
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范:

```bash
# 格式
<type>(<scope>): <subject>

# 类型
feat:     新功能
fix:      修复 bug
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构
perf:     性能优化
test:     测试相关
build:    构建系统
ci:       CI 配置
chore:    其他杂项

# 示例
git commit -m "feat(auth): add JWT token refresh endpoint"
git commit -m "fix(firewall): resolve memory leak in XDP program"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(vehicle): simplify connection handling"
git commit -m "test(cloud): add integration tests for rule service"
```

## CI/CD

项目使用 GitHub Actions 进行持续集成和部署。详细文档参考 [GitHub Actions 配置指南](./GITHUB_ACTIONS.md)。

### 工作流概览

1. **Vehicle CI** - 车端构建和测试
2. **Cloud CI** - 云端构建和测试
3. **Frontend CI** - 前端构建和测试
4. **Deploy** - 自动部署

### 本地测试 CI

```bash
# 模拟 CI 环境
make clean
make build
make test
make lint

# 或使用 act 本地运行 GitHub Actions
act -j test
```

### 触发条件

- Push 到 `main` 或 `develop`
- 创建 Pull Request
- 手动触发部署

## 开发工具

### IDE 推荐

- **车端 (C)**: VSCode + C/C++ Extension, CLion
- **云端 (Python)**: VSCode + Python Extension, PyCharm
- **前端 (TypeScript/React)**: VSCode + ESLint + Prettier

### VSCode 扩展

创建 `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-vscode.cpptools",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "eamodio.gitlens",
    "github.copilot"
  ]
}
```

### 终端工具

- **终端复用**: tmux, screen
- **HTTP 客户端**: curl, httpie, Postman
- **数据库客户端**: DBeaver, MySQL Workbench
- **Git GUI**: GitKraken, SourceTree
- **容器管理**: Portainer, Lazydocker

### 开发脚本

创建个人开发脚本 `dev.sh`:

```bash
#!/bin/bash
# 个人开发环境启动脚本

# 启动数据库
make dev-up

# 等待服务就绪
sleep 10

# 启动云端服务（后台）
cd cloud
make dev-auth &
make dev-rule &
make dev-log &
make dev-vehicle &

# 启动前端
cd ../frontend
make dev
```

## 故障排除

### Docker 相关

#### 容器无法启动

```bash
# 检查 Docker 服务
sudo systemctl status docker

# 重启 Docker
sudo systemctl restart docker

# 查看容器日志
make dev-logs

# 重新构建容器
docker compose up -d --build
```

#### 端口冲突

```bash
# 检查端口占用
netstat -tulpn | grep 3306   # MySQL
netstat -tulpn | grep 5001   # 认证服务

# 停止冲突服务或修改端口
docker compose down
```

### Python 相关

#### uv 命令未找到

```bash
# 重新安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 配置 PATH
source $HOME/.cargo/env
```

#### 依赖安装失败

```bash
# 清理缓存
uv cache clean

# 重新同步
cd cloud
make clean
make install-dev
```

### 车端相关

#### 交叉编译失败

```bash
# 安装交叉编译工具
sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# 检查工具链
aarch64-linux-gnu-gcc --version
```

#### CMake 错误

```bash
# 清理构建目录
cd vehicle
make clean-all

# 重新构建
make build
```

### 前端相关

#### npm install 失败

```bash
# 清理缓存
cd frontend
make clean-cache

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
make install
```

#### 构建错误

```bash
# 清理构建产物
make clean

# 重新构建
make build
```

### 权限问题

```bash
# 添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 修改文件所有者
sudo chown -R $USER:$USER .
```

### 性能问题

```bash
# 检查系统资源
htop
docker stats

# 清理 Docker 资源
docker system prune -a

# 限制容器资源
# 编辑 docker compose.yml 添加资源限制
```

## 参考资源

### 项目文档

- [项目 README](../README.md)
- [Makefile 使用指南](./MAKEFILE.md)
- [uv 使用指南](./UV_GUIDE.md)
- [GitHub Actions 配置](./GITHUB_ACTIONS.md)
- [产品需求文档](../specs/0001-prd.md)
- [详细设计文档](../specs/0002-design.md)
- [实施计划](../specs/0003-implementation-plan.md)

### API 文档

- [认证服务 API](http://localhost:5001/api/docs)
- [规则服务 API](http://localhost:5002/api/docs)
- [日志服务 API](http://localhost:5003/api/docs)
- [车辆管理 API](http://localhost:5004/api/docs)

### 外部资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [React 文档](https://react.dev/)
- [uv 文档](https://docs.astral.sh/uv/)
- [CMake 文档](https://cmake.org/documentation/)
- [Docker 文档](https://docs.docker.com/)

### 获取帮助

- **GitHub Issues**: https://github.com/your-org/idps/issues
- **讨论区**: https://github.com/your-org/idps/discussions
- **技术支持**: support@idps.example.com
- **文档中心**: https://docs.idps.example.com

## 贡献指南

欢迎贡献！请参考以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码审查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] CI 检查通过
- [ ] 没有引入新的警告

---

**最后更新**: 2026-01-14

如有问题或建议，请提交 Issue 或联系维护团队。
